import json
from langchain_core.documents.base import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.graph import CompiledGraph
from typing_extensions import TypedDict
from typing import List, Dict, Annotated, Any
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver

# Function to add messages, ensuring new messages are appended
def add_messages(left: List[Any], right: List[Any]) -> List[Any]:
    """Adds messages to the state, ensuring history is preserved."""
    return left + right

# Function to combine retrieved context documents
def combine_documents(left: List[Document], right: List[Document]) -> List[Document]:
    """Combines lists of documents."""
    return left + right

class GraphState (TypedDict):
    """
    Represents the state of the RAG graph.
    """
    messages: Annotated[list, add_messages]
    retrieved_context: Annotated[List[Document], combine_documents] # Accumulate context
    recommended_topics: List[str] # List of topics the LLM recommends for retrieval
    current_retrieval_index: int # Index of the topic being retrieved in recommended_topics
    first_message: bool # Flag for the first message in a session (can be removed if not needed)

def normalize_topic(topic: str) -> str:
    """
    Converts the input topic string to lowercase and strips whitespace.
    """
    return topic.lower().strip()

def remove_context_placeholder(prompt: str) -> str:
    """
    Remove the '{context}' placeholder from a prompt string.
    """
    return prompt.replace("{context}", "").strip()

def get_pipeline_rag (
    vectorstore_config: Dict[str, str],
    memory_filepath: str,
    api_key: str | None = None,
    system_prompt_text: str = (
        'You are a helpful teacher helping a student with course material.\n'
        'You will answer a question based on the context provided:\n'
        'Don\'t answer questions about other things.\n\n'
        '{context}\n'
    ),
    model: str = 'gpt-4o-mini'
) -> CompiledGraph:
    """
    Create a dynamic retrieval-augmented generation (RAG) graph that includes multi-topic
    recommendation, iterative retrieval from relevant vectorstores, and answer generation.
    The returned object is a compiled graph (with memory checkpoint) that you can run by
    providing an initial state.

    Args:
        vectorstore_config (Dict[str, str]): Mapping of topic name (folder name) to vectorstore path.
                                              *WARNING* TOPIC MUST BE ALL LOWER CASE
        memory_filepath (str): Path for the memory checkpoint (SQLite database).
        api_key (Optional[str]): API key for language models and embeddings.
        system_prompt_text (str): System prompt template for answer generation.
        model (str): Model name to use for LLM calls.

    Returns:
        CompiledGraph: A compiled state graph ready for execution.
    """

    # Initialize FAISS retrievers for each topic
    # (i.e., load each vectorstore to be used when it is needed)
    retrievers = {}
    for topic, vstore_path in vectorstore_config.items():
        retrievers[topic] = FAISS.load_local(
            vstore_path,
            OpenAIEmbeddings(api_key=api_key) if api_key else OpenAIEmbeddings(),
            allow_dangerous_deserialization=True
        ).as_retriever()

    # Initialize LLM for all operations
    llm = ChatOpenAI(model=model, temperature=0, api_key=api_key) if api_key else ChatOpenAI(model=model, temperature=0)

    # Build the Chain for the generate node
    # The 'input' placeholder is for the latest user message
    # The 'messages' placeholder is for the conversation history excluding the latest input
    generate_chain = ChatPromptTemplate.from_messages([
        ('system', system_prompt_text),
        MessagesPlaceholder('messages'), # This will be the chat history up to the current turn
        ('human', "{input}") # The current user query
    ]) | llm | StrOutputParser()

    # Helper function to format topic keys for prompts
    def format_topic_keys(topics: Dict[str, str]) -> str:
        keys = list(topics.keys())
        if not keys:
            return ""
        elif len(keys) == 1:
            return f"'{keys[0]}'"
        else:
            return ", ".join(f"'{key}'" for key in keys[:-1]) + f", or '{keys[-1]}'"

    # Node: Determine Relevant Topics
    def determine_relevant_topics_node(state: GraphState) -> Dict[str, Any]:
        """
        Determines 1-3 relevant topics from the available vectorstores based on the user's query.
        """
        user_question = state["messages"][-1]
        available_topics = vectorstore_config.keys()
        formatted_topics = format_topic_keys(vectorstore_config)

        # Prompt for LLM to identify relevant topics
        topic_identification_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an assistant that identifies relevant topics for information retrieval. "
             "Given a user's question, identify 1 to 3 topics from the following list that are most relevant. "
             "Your response should be a comma-separated list of the relevant topic names, "
             "e.g., 'homework, labs'. If no topics are relevant, respond with 'none'."
             f"Available topics: {formatted_topics}."
            ),
            ("human", "User question: {question}\nRelevant topics:")
        ])

        # Invoke LLM to get recommended topics
        # Assuming user_question is a HumanMessage or similar, we need its content
        question_content = user_question.content if isinstance(user_question, (HumanMessage, SystemMessage)) else str(user_question)
        response = llm.invoke(topic_identification_prompt.format_messages(question=question_content))

        # Parse the LLM's response
        raw_topics = response.content.split(',')
        recommended_topics = []
        for topic in raw_topics:
            normalized_t = normalize_topic(topic)
            if normalized_t in available_topics and normalized_t != "none":
                recommended_topics.append(normalized_t)
        
        # Ensure only 1-3 topics are selected, if more are returned by LLM, prioritize first 3
        recommended_topics = recommended_topics[:3] if recommended_topics else []

        print(f"Recommended topics: {recommended_topics}")
        # Initialize retrieved_context here for the new turn
        return {"recommended_topics": recommended_topics, "current_retrieval_index": 0, "retrieved_context": []}

    # Node: Retrieve and Accumulate Context
    def retrieve_and_accumulate_node(state: GraphState) -> Dict[str, Any]:
        """
        Retrieves context for the current topic in the recommended_topics list
        and accumulates it in the retrieved_context.
        """
        recommended_topics = state["recommended_topics"]
        current_index = state["current_retrieval_index"]
        user_question = state["messages"][-1]
        
        # Ensure user_question is a string for the retriever
        question_content = user_question.content if isinstance(user_question, (HumanMessage, SystemMessage)) else str(user_question)

        # retrieved_context is automatically managed by the Annotated `combine_documents`
        # We retrieve, and the annotation handles adding it to the state's `retrieved_context`
        retrieved_docs_for_current_step = []

        if current_index < len(recommended_topics):
            topic_to_retrieve = recommended_topics[current_index]
            print(f"Retrieving from topic: {topic_to_retrieve}")
            
            # Check if retriever exists for the topic
            if topic_to_retrieve in retrievers:
                # Perform retrieval for the current topic
                documents: List[Document] = retrievers[topic_to_retrieve].invoke(question_content)
                retrieved_docs_for_current_step.extend(documents)
            else:
                print(f"Warning: No retriever found for topic '{topic_to_retrieve}'")

            # Increment index for the next retrieval iteration
            next_index = current_index + 1
        else:
            # This case should ideally not be reached if route_retrieval is correct
            print("No more topics to retrieve or index out of bounds.")
            next_index = current_index # Don't increment if already at end

        return {
            "retrieved_context": retrieved_docs_for_current_step, # This will be combined with previous context
            "current_retrieval_index": next_index
        }

    # Node: Answer Generation
    def generate_node(state: GraphState) -> Dict[str, Any]:
        """
        Generates the final answer using the accumulated context and chat history.
        """
        messages = state["messages"]
        documents = state.get("retrieved_context", [])

        # The 'input' to the chain is the latest user message
        # The 'messages' to the chain is the entire chat history *excluding* the latest user message
        generation = generate_chain.invoke({
            "context": documents,
            "input": messages[-1], # Current user query
            "messages": messages[:-1], # Previous chat history
        })
        
        # Update conversation history with the generated answer
        return {"messages": messages + [generation]}

    # Conditional router for iterative retrieval
    def route_retrieval(state: GraphState) -> str:
        """
        Routes the graph based on whether more topics need to be retrieved.
        """
        if state["current_retrieval_index"] < len(state["recommended_topics"]):
            return "retrieve_and_accumulate" # Continue looping to retrieve more topics
        else:
            return "generate" # All relevant topics retrieved, proceed to generate answer

    # Build the state graph.
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("determine_relevant_topics", determine_relevant_topics_node)
    graph.add_node("retrieve_and_accumulate", retrieve_and_accumulate_node)
    graph.add_node("generate", generate_node)

    # Define the flow
    graph.add_edge(START, "determine_relevant_topics")
    
    # Conditional edge after determining topics
    # If no topics are recommended, directly go to generate (potentially with no context)
    # Otherwise, start the iterative retrieval loop
    graph.add_conditional_edges(
        "determine_relevant_topics",
        lambda state: "generate" if not state.get("recommended_topics") else "retrieve_and_accumulate"
    )

    # Conditional edge for the iterative retrieval loop
    graph.add_conditional_edges(
        "retrieve_and_accumulate",
        route_retrieval
    )
    
    # Final edge to END after generation
    graph.add_edge("generate", END)

    # Set up memory checkpoint using SQLite.
    memory = SqliteSaver.from_conn_string(memory_filepath)
    compiled_graph: CompiledGraph = graph.compile(checkpointer=memory)
    return compiled_graph