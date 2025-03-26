"""
Module for creating a simple retrieval-augmented generation (RAG) graph using LangChain.

© 2024 Blaine Freestone, Carson Bush

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
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver

class GraphState (TypedDict):
    messages: List[str]
    current_topic: str | None = None
    retrieved_context: List[Document] | None = None
    first_messsage: bool = True

def ensure_state_defaults(func):
    def wrapper(state, *args, **kwargs):
        if not state["first_messsage"]:
            state["first_messsage"] = True
        return func(state, *args, **kwargs)
    return wrapper

def normalize_topic(topic: str) -> str:
    """
    Converts the input topic string to lowercase.

    Args:
        topic (str): The topic string to be normalized.

    Returns:
        str: The normalized topic string in lowercase.
    """
    return topic.lower()

def get_pipeline_rag (
    vectorstore_config: Dict[str, str],
    memory_filepath: str,
    api_key: str | None = None,
    system_prompt_text: str = (
        'You are a helpful teacher helping a student with course material.\n'
        'Answer the question based on the provided course content:\n\n'
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
    # (i.e load each vectorestore to be used when it is needed)
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

    # Node: initial topic extraction, establish the initial topic for the chat
    @ensure_state_defaults
    def initial_topic_node(state: GraphState, vectorstore_config: Dict) -> dict:
        if not state.get("first_messsage"):
            state["first_messsage"] = False
            formatted_topics = format_topic_keys(vectorstore_config)
            establish_topic = ChatPromptTemplate.from_messages([
                ("system", f"You are an assistant who extracts a concise topic label from a user's explanation. "
                            f"Choose one of these topics (it is vital to match case and letters exactly): {formatted_topics}. If you can't extract a topic default to the first topic."),
                ("human", "User message: {question}\nExtract the topic:")
            ])
            question = state["messages"][-1]
            formatted_prompt = establish_topic.format(question=question)
            llm_topic = ChatOpenAI(model=model, temperature=0) if api_key is None else ChatOpenAI(api_key=api_key, model=model, temperature=0)
            result = llm_topic.invoke([SystemMessage(content=formatted_prompt)])
            topic = normalize_topic(result.content)
            return {"current_topic": topic}
        return {"current_topic": state.get("current_topic")}
    
    # Node: routing to update or to maintain the current topic
    def routing_node(state: StateGraph, vectorstore_config: Dict) -> dict:
        if not state.get("first_messsage"):
            formatted_topics = format_topic_keys(vectorstore_config)
            current_topic = state.get("current_topic")
            # If there's no valid current topic, do nothing (or optionally signal an error)
            if not current_topic or current_topic not in vectorstore_config:
                raise ValueError(f"Invalid topic '{current_topic}' encountered in state. Please ensure a valid topic is set.")
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"You are monitoring the conversation. The current topic is '{current_topic}'. "
                        f"Using these topics exactly ({formatted_topics}), if the user's latest message indicates a change, "
                        f"output the new topic; otherwise, repeat the current topic."),
                ("human", "User message: {question}\nCurrent topic: {current_topic}\nNew topic:")
            ])
            question = state["messages"][-1]
            formatted = prompt.format(question=question, current_topic=current_topic)
            llm_route = ChatOpenAI(model=model, temperature=0) if api_key is None else ChatOpenAI(api_key=api_key, model=model, temperature=0)
            result = llm_route.invoke([SystemMessage(content=formatted)])
            new_topic = normalize_topic(result.content)
            # If the new topic is invalid, retain the current topic.
            if new_topic not in vectorstore_config:
                new_topic = current_topic
            return {"current_topic": new_topic}
        else:
            state["first_messsage"] = False
            return {"current_topic": state.get("current_topic")}


    
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
    graph.add_node("initial_topic", lambda state: initial_topic_node(state, vectorstore_config))
    graph.add_node("routing", lambda state: routing_node(state, vectorstore_config))

    # Add retrieval nodes for each topic.
    for topic in vectorstore_config.keys():
        node_name = f"retrieve_{topic}"
        graph.add_node(node_name, make_retrieval_node(topic))

    graph.add_node("generate", generate_node)

    # Define the flow: START → initial_topic → routing → conditional retrieval → generate → END.
    graph.add_edge(START, "initial_topic")
    graph.add_edge("initial_topic", "routing")
    graph.add_conditional_edges("routing", lambda state: state["current_topic"], vectorstore_nodes)
    for node in vectorstore_nodes.values():
        graph.add_edge(node, "generate")
    graph.add_edge("generate", END)

    # Set up memory checkpoint using SQLite.
    memory = SqliteSaver.from_conn_string(f"{memory_filepath}")
    compiled_graph: CompiledGraph = graph.compile(checkpointer=memory)
    return compiled_graph
