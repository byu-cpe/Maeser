"""
Module for creating a simple retrieval-augmented generation (RAG) graph using LangChain.

© 2024 Gohaun Manley

This file is part of Maeser.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""
from langchain_core.documents.base import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph.graph import CompiledGraph
from typing_extensions import TypedDict
from typing import List, Dict, Annotated
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver

def add_messages(left: List[str], right: List[str]) -> List[str]:
    return left + right

class GraphState (TypedDict):
    messages: Annotated[list, add_messages]
    current_topic: str
    retrieved_context: List[Document]
    first_messsage: bool

def normalize_topic(topic: str) -> str:
    """
    Converts the input topic string to lowercase.
    """
    return topic.lower()

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
    Create a dynamic retrieval-augmented generation (RAG) graph that includes topic extraction,
    conditional routing to retrieval nodes, and answer generation. The returned object is a
    compiled graph (with memory checkpoint) that you can run by providing an initial state.
    
    Args:
        vectorstore_config (Dict[str, Tuple[str, str]]): Mapping of topic to (vectorstore_path, index name) *WARNING* TOPIC MUST BE ALL LOWER CASE
        memory_filepath (str): Path for the memory checkpoint (SQLite database).
        api_key (Optional[str]): API key for language models and embeddings.
        system_prompt_text (str): System prompt template for answer generation.
        model (str): Model name to use.
    
    Returns:
        CompiledGraph: A compiled state graph ready for execution.
    """

    # initalize FAISS retreivers for each topic 
    # (i.e load each vectorstore to be used when it is needed)
    retrievers = {}
    for topic, vstore_path in vectorstore_config.items():
        retrievers[topic] = FAISS.load_local(
            vstore_path,
            OpenAIEmbeddings() if api_key is None else OpenAIEmbeddings(api_key=api_key),
            allow_dangerous_deserialization=True
        ).as_retriever()

    # Build the Chain for the generate node
    system_prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt_text),
        MessagesPlaceholder('messages'),
        ('human', "{input}")
    ])
    llm = ChatOpenAI(model=model, temperature=0) if api_key is None else ChatOpenAI(api_key=api_key, model=model, temperature=0)
    chain = system_prompt | llm | StrOutputParser()

    #format topics for later topic extraction
    def format_topic_keys(topics):
        keys = list(topics.keys())  # Get dictionary keys as a list
        if not keys:
            return ""  # Return empty string if dictionary is empty
        elif len(keys) == 1:
            return f"'{keys[0]}'"  # If only one key, return it without "or"
        else:
            return ", ".join(f"'{key}'" for key in keys[:-1]) + f", or '{keys[-1]}'"

    def determine_topic_node (state: GraphState, vectorstore_config: Dict) -> dict:

        # Prepare the list of valid topics plus "off topic"
        formatted_topics = format_topic_keys(vectorstore_config)
        current_topic = state.get("current_topic")

        # Build a prompt that includes the current topic (if any) and the user message.
        clean_system_prompt = remove_context_placeholder(system_prompt_text)
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"You are an assistant who extracts a concise topic label from a user's explanation. Here is the Current Topic: {current_topic}. If the Current Topic is None, please choose a valid topic."
                       f"The AI who will be answering the users questions and using your topics has been given this prompt {clean_system_prompt}. Please use this as part of your consideration for the topic."
                       f"Using these topics exactly ({formatted_topics}), if the user's latest message indicates that the topic should change, "
                       f"output the new topic; otherwise, repeat the current topic."),
            ("human", "User message: {question}\nExtract the topic:")
        ])

        question = state["messages"][-1]
        formatted_prompt = prompt_template.format(question=question, current_topic=current_topic if current_topic else "None")
        llm_topic = ChatOpenAI(model=model, temperature=0) if api_key is None else ChatOpenAI(api_key=api_key, model=model, temperature=0)
        result = llm_topic.invoke([SystemMessage(content=formatted_prompt)])
        topic = normalize_topic(result.content)
        return {"current_topic": topic}
    
    # Create a factory for retrieval nodes to return relevant information
    def make_retrieval_node(topic: str):
        def retrieval_node(state: GraphState) -> dict:
            question = state["messages"][-1]
            documents: List[Document] = retrievers[topic].invoke(question)
            return {"retrieved_context": documents}
        return retrieval_node
    
    # Map topics with retrieval node names
    vectorstore_nodes = {}
    for topic in vectorstore_config.keys():
        node_name = f"retrieve_{topic}"
        vectorstore_nodes[topic] = node_name

    # Node: answer generation.
    def generate_node(state: GraphState) -> dict:
        messages = state["messages"]
        documents = state.get("retrieved_context", [])
        generation = chain.invoke({
            "context": documents,
            "input": messages[-1],
            "messages": messages[:-1],
        })
        # Update conversation history with the generated answer.
        return {"messages": messages + [generation]}
    
    # Build the state graph.
    graph = StateGraph(GraphState)
    graph.add_node("determine_topic", lambda state: determine_topic_node(state, vectorstore_config))    

    # Set up conditional branching based on the determined topic.
    # Mapping: if "off topic", go to off_topic_response; if valid topic, go to its retrieval node.
    mapping = {}
    for topic in vectorstore_config.keys():
        mapping[topic] = f"retrieve_{topic}"
    graph.add_conditional_edges("determine_topic", lambda state: state["current_topic"], mapping)
    
    # Add retrieval nodes for each valid topic.
    for topic in vectorstore_config.keys():
        node_name = f"retrieve_{topic}"
        graph.add_node(node_name, make_retrieval_node(topic))
        graph.add_edge(node_name, "generate")
    
    # Add answer generation node.
    graph.add_node("generate", generate_node)
    
    # Define the overall flow.
    graph.add_edge(START, "determine_topic")
    graph.add_edge("generate", END)
    
    # Set up memory checkpoint using SQLite.
    memory = SqliteSaver.from_conn_string(f'{memory_filepath}')
    compiled_graph: CompiledGraph = graph.compile(checkpointer=memory)
    return compiled_graph