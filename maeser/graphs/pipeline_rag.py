# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Module for creating a pipeline **Retrieval-Augmented Generation (RAG) graph** using LangChain.

This RAG graph accepts multiple vector stores, allowing the chatbot to dynamically choose the
most relevant vector store when answering a user's question. However, only one vector store can
be accessed per response.

    **Note:** In almost all cases, **universal_rag** is a better option compared to **pipeline_rag**.
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


def _add_messages(left: List[str], right: List[str]) -> List[str]:
    """Ensures that items assigned to a list with this annotation are added instead of directly assigned.

    Args:
        left (list): The old list.
        right (list): The new list containing the new item.

    Returns:
        None
    """
    return left + right


class _GraphState(TypedDict):
    """Represents the state of the graph.

    Attributes:
        messages (Annotated[list, _add_messages]): The messages in the conversation.
        current_topic (str): The last topic/vector store that was used for context retrieval.
        retrieved_context (List[Document]): The context retrieved from the vector store.
        first_message (bool): Whether or not this is the first message being generated.
    """

    messages: Annotated[list, _add_messages]
    current_topic: str
    retrieved_context: List[Document]
    first_messsage: bool


def _normalize_topic(topic: str) -> str:
    """
    Converts the input topic string to lowercase.

    Args:
        topic (str): The topic to be normalized.

    Returns:
        str: The normalized topic.
    """
    return topic.lower()


def _remove_context_placeholder(prompt: str) -> str:
    """
    Remove the '{context}' placeholder from a prompt string.

    Args:
        prompt (str): The prompt to be formatted.

    Returns:
        str: The prompt with '{context}' removed.
    """
    return prompt.replace("{context}", "").strip()


def get_pipeline_rag(
    vectorstore_config: Dict[str, str],
    memory_filepath: str,
    api_key: str | None = None,
    system_prompt_text: str = (
        "You are a helpful teacher helping a student with course material.\n"
        "You will answer a question based on the context provided.\n"
        "If the question is unrelated to the topic or the context, "
        "politely inform the user that their question is outside the context of your resources.\n\n"
        "{context}\n"
    ),
    model: str = "gpt-4o-mini",
) -> CompiledGraph:
    """
    Creates a pipeline **Retrieval-Augmented Generation (RAG)** graph.

        **Note:** In almost all cases, **universal_rag.get_universal_rag()** is a better option compared to **pipeline_rag.get_pipeline_rag()**.

    A pipeline RAG graph is a dynamic **Retrieval-Augmented Generation (RAG)** graph that includes topic extraction,
    conditional routing to retrieval nodes, and answer generation. The returned object is a
    compiled graph (with memory checkpoint).

    This RAG graph accepts multiple vector stores, allowing the chatbot to dynamically choose the
    most relevant vector store when answering a user's question. However, only one vector store can
    be accessed per response.

    The following system prompt is used if none is provided:

        \"\"\"You are a helpful teacher helping a student with course material.
        You will answer a question based on the context provided.
        If the question is unrelated to the topic or the context, politely inform the user that their question is outside the context of your resources.

        {context}
        \"\"\"

    Args:
        vectorstore_config (Dict[str, str]):
            Mapping of topic name to vector store path.

                > **WARNING:** The topic name must be **all lower case** due to limitations with the current implementation.

        memory_filepath (str): Path for the memory checkpoint (SQLite database).
        api_key (str | None): API key for the language model. Defaults to None,
            in which case it will use the ``OPENAI_API_KEY`` environment variable.
        system_prompt_text (str): System prompt template for answer generation. Defaults to a helpful teacher prompt.
        model (str): Model name to use. Defaults to 'gpt-4o-mini'.

    Returns:
        CompiledGraph: A compiled state graph (with memory checkpoint) ready for execution.
    """

    # initialize FAISS retrievers for each topic
    # (i.e load each vector store to be used when it is needed)
    retrievers = {}
    for topic, vstore_path in vectorstore_config.items():
        retrievers[topic] = FAISS.load_local(
            vstore_path,
            OpenAIEmbeddings()
            if api_key is None
            else OpenAIEmbeddings(api_key=api_key),
            allow_dangerous_deserialization=True,
        ).as_retriever()

    # Build the Chain for the generate node
    system_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_text),
            MessagesPlaceholder("messages"),
            ("human", "{input}"),
        ]
    )
    llm = (
        ChatOpenAI(model=model, temperature=0)
        if api_key is None
        else ChatOpenAI(api_key=api_key, model=model, temperature=0)
    )
    chain = system_prompt | llm | StrOutputParser()

    # format topics for later topic extraction
    def format_topic_keys(topics):
        keys = list(topics.keys())  # Get dictionary keys as a list
        if not keys:
            return ""  # Return empty string if dictionary is empty
        elif len(keys) == 1:
            return f"'{keys[0]}'"  # If only one key, return it without "or"
        else:
            return ", ".join(f"'{key}'" for key in keys[:-1]) + f", or '{keys[-1]}'"

    def determine_topic_node(state: _GraphState, vectorstore_config: Dict) -> dict:
        # Prepare the list of valid topics plus "off topic"
        formatted_topics = format_topic_keys(vectorstore_config)
        current_topic = state.get("current_topic")

        # Build a prompt that includes the current topic (if any) and the user message.
        clean_system_prompt = _remove_context_placeholder(system_prompt_text)
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are an assistant who extracts a concise topic label from a user's explanation. Here is the Current Topic: {current_topic}."
                    f"For context, a separate AI who will be answering the users questions and using your topics has been given the following prompt:"
                    f"===== CONTEXT ====="
                    f"{clean_system_prompt}."
                    f"==================="
                    f"Use the prompt above as context, but ignore the response instructions. Instead, follow these response guidelines:"
                    f"Using these topics exactly ({formatted_topics}), if the user's latest message indicates that the topic should change, "
                    f"output the new topic."
                    f"If the Current Topic is None, please choose a valid topic."
                    f"If none of the topics match, choose the first topic."
                    f"In any other case, repeat the current topic."
                    f"In all cases, your topic should exactly match one of the topics listed.",
                ),
                ("human", "User message: {question}\nExtract the topic:"),
            ]
        )

        question = state["messages"][-1]
        formatted_prompt = prompt_template.format(
            question=question, current_topic=current_topic if current_topic else "None"
        )
        llm_topic = (
            ChatOpenAI(model=model, temperature=0)
            if api_key is None
            else ChatOpenAI(api_key=api_key, model=model, temperature=0)
        )
        result = llm_topic.invoke([SystemMessage(content=formatted_prompt)])
        topic = _normalize_topic(result.content)

        # Edge case handling
        topic = (
            topic if topic in vectorstore_config.keys() else current_topic
        )  # Case where topic is not in in list of topics
        topic = (
            topic if topic is not None else list(vectorstore_config.keys())[0]
        )  # Case where topic is none (may happen on first response)

        return {"current_topic": topic}

    # Create a factory for retrieval nodes to return relevant information
    def make_retrieval_node(topic: str):
        def retrieval_node(state: _GraphState) -> dict:
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
    def generate_node(state: _GraphState) -> dict:
        messages = state["messages"]
        documents = state.get("retrieved_context", [])
        generation = chain.invoke(
            {
                "context": documents,
                "input": messages[-1],
                "messages": messages[:-1],
            }
        )
        # Update conversation history with the generated answer.
        return {"messages": [generation]}

    # Build the state graph.
    graph = StateGraph(_GraphState)
    graph.add_node(
        "determine_topic", lambda state: determine_topic_node(state, vectorstore_config)
    )

    # Set up conditional branching based on the determined topic.
    # Mapping: if "off topic", go to off_topic_response; if valid topic, go to its retrieval node.
    mapping = {}
    for topic in vectorstore_config.keys():
        mapping[topic] = f"retrieve_{topic}"
    graph.add_conditional_edges(
        "determine_topic", lambda state: state["current_topic"], mapping
    )

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
    memory = SqliteSaver.from_conn_string(f"{memory_filepath}")
    compiled_graph: CompiledGraph = graph.compile(checkpointer=memory)
    return compiled_graph
