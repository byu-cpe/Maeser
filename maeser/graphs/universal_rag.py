# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Module for creating a universal **Retrieval-Augmented Generation (RAG) graph** using LangChain.

This RAG graph accepts multiple vector stores, like **pipeline_rag**, but also pulls from
as many vector stores as needed (or none at all) per response.

Attributes:
    recommended_topics (List[str]): The list of recommended topics/vectorstores from the last user request.
"""

from langchain_core.documents.base import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from typing_extensions import TypedDict
from typing import List, Dict, Annotated, Any
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver
import tiktoken

_enc = tiktoken.encoding_for_model("gpt-4o")


def _add_messages(left: List[Any], right: List[Any]) -> List[Any]:
    return left + right


def _combine_documents(left: List[Document], right: List[Document]) -> List[Document]:
    return left + right


class _GraphState(TypedDict):
    messages: Annotated[list, _add_messages]
    retrieved_context: Annotated[List[Document], _combine_documents]
    recommended_topics: List[str]
    current_retrieval_index: int
    first_message: bool
    previous_question: str
    previous_topics: List[str]
    chat_summary: str


def _normalize_topic(topic: str) -> str:
    return topic.lower().strip()


def _format_topic_keys(topics: Dict[str, str]) -> str:
    keys = list(topics.keys())
    if not keys:
        return ""
    elif len(keys) == 1:
        return f"'{keys[0]}'"
    else:
        return ", ".join(f"'{key}'" for key in keys[:-1]) + f", or '{keys[-1]}'"


def get_universal_rag(
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
    """Creates a universal **Retrieval-Augmented Generation (RAG)** graph.

    This RAG graph pulls from as many vector stores as needed (or none at all) to generate a response.
    The vector stores are chosen based on relevance to the user's input, and context from these
    vectorstores are used along with a summary of recent chat history as input for response generation.

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
        CompiledGraph: _description_
    """
    retrievers = {
        topic: FAISS.load_local(
            path,
            OpenAIEmbeddings(api_key=api_key) if api_key else OpenAIEmbeddings(),
            allow_dangerous_deserialization=True,
        ).as_retriever()
        for topic, path in vectorstore_config.items()
    }

    llm = (
        ChatOpenAI(model=model, temperature=0, api_key=api_key)
        if api_key
        else ChatOpenAI(model=model, temperature=0)
    )

    generate_chain = (
        ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_text),
                MessagesPlaceholder("messages"),
                ("human", "{input}"),
            ]
        )
        | llm
        | StrOutputParser()
    )

    def determine_relevant_topics_node(state: _GraphState) -> Dict[str, Any]:
        user_question = state["messages"][-1]
        question_content = getattr(user_question, "content", user_question)

        available_topics = vectorstore_config.keys()
        formatted_topics = _format_topic_keys(vectorstore_config)

        topic_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are an assistant that identifies relevant topics for information retrieval. Given a user's question, identify 1 to 3 topics from the following list that are most relevant. Respond with a comma-separated list. Available topics: {formatted_topics}.",
                ),
                ("human", "{question}"),
            ]
        )

        print(
            "Question content passed to topic prompt:", question_content
        )  # Debug print

        response = llm.invoke(topic_prompt.format_messages(question=question_content))
        raw_topics = response.content.split(",")
        global recommended_topics
        recommended_topics = [
            _normalize_topic(t)
            for t in raw_topics
            if _normalize_topic(t) in available_topics and _normalize_topic(t) != "none"
        ]

        print(
            "Recommended topics:", recommended_topics
        )  # Print recommended topics to console

        return {
            "recommended_topics": recommended_topics[:3],
            "current_retrieval_index": 0,
            "retrieved_context": [],
            "previous_question": question_content,
            "previous_topics": recommended_topics[:3],
        }

    def retrieve_and_accumulate_node(state: _GraphState) -> Dict[str, Any]:
        topics = state.get("recommended_topics", [])
        idx = state.get("current_retrieval_index", 0)
        if not state["messages"]:
            print("No messages found in retrieve_and_accumulate_node")
            return {"retrieved_context": [], "current_retrieval_index": idx}
        user_question = state["messages"][-1]
        question_content = getattr(user_question, "content", user_question)

        docs = []
        if idx < len(topics):
            topic = topics[idx]
            if topic in retrievers:
                docs = retrievers[topic].invoke(question_content)

        return {"retrieved_context": docs, "current_retrieval_index": idx + 1}

    def generate_node(state: _GraphState) -> Dict[str, Any]:
        if not state["messages"]:
            print("No messages found in generate_node")
            return {"messages": []}

        messages = state["messages"]
        docs = state.get("retrieved_context", [])
        summary = state.get("chat_summary", "")

        # Input to the chain
        result = generate_chain.invoke(
            {
                "context": docs,
                "input": getattr(messages[-1], "content", messages[-1]),
                "messages": messages[:-1] + [summary] if summary else messages[:-1],
            }
        )

        # Log token usage
        def count_tokens(msgs):
            content = ""
            for m in msgs:
                content += getattr(m, "content", str(m))
            return len(_enc.encode(content))

        return {"messages": [result]}

    def summarize_chat_history_node(state: _GraphState) -> Dict[str, Any]:
        messages = state.get("messages", [])
        if len(messages) < 3:
            return {"chat_summary": ""}
        recent_messages = messages[-3:]
        recent_content = [getattr(m, "content", m) for m in recent_messages]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Summarize useful and relevant information from this chat history, discarding off-topic parts.",
                ),
                (
                    "human",
                    f"Messages:\n{recent_content}\n\nOutput a concise useful summary.",
                ),
            ]
        )

        summary = llm.invoke(prompt.format_messages())
        return {"chat_summary": summary.content}

    def is_message_related_to_previous_node(state: _GraphState) -> Dict[str, Any]:
        if not state["messages"]:
            print("No messages found in is_message_related_to_previous_node")
            return {
                "recommended_topics": [],
                "current_retrieval_index": 0,
                "retrieved_context": [],
            }
        current_question = getattr(
            state["messages"][-1], "content", state["messages"][-1]
        )
        previous_question = state.get("previous_question", "")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Determine if these two questions are topically related."),
                (
                    "human",
                    f"Previous question: {previous_question}\nCurrent question: {current_question}\nRespond with only 'yes' or 'no'.",
                ),
            ]
        )

        response = llm.invoke(prompt.format_messages())
        related = "yes" in response.content.lower()

        if related and state.get("previous_topics"):
            return {
                "recommended_topics": state["previous_topics"],
                "current_retrieval_index": 0,
                "retrieved_context": [],
            }
        else:
            return {
                "recommended_topics": [],
                "current_retrieval_index": 0,
                "retrieved_context": [],
            }

    def route_retrieval(state: _GraphState) -> str:
        return (
            "retrieve_and_accumulate"
            if state.get("current_retrieval_index", 0)
            < len(state.get("recommended_topics", []))
            else "generate"
        )

    graph = StateGraph(_GraphState)

    graph.add_node("check_related", is_message_related_to_previous_node)
    graph.add_node("determine_relevant_topics", determine_relevant_topics_node)
    graph.add_node("summarize_chat", summarize_chat_history_node)
    graph.add_node("retrieve_and_accumulate", retrieve_and_accumulate_node)
    graph.add_node("generate", generate_node)

    graph.add_edge(START, "determine_relevant_topics")
    graph.add_edge("determine_relevant_topics", "summarize_chat")
    graph.add_conditional_edges(
        "summarize_chat",
        lambda s: "generate"
        if not s.get("recommended_topics")
        else "retrieve_and_accumulate",
    )
    graph.add_conditional_edges("retrieve_and_accumulate", route_retrieval)
    graph.add_edge("generate", END)

    memory = SqliteSaver.from_conn_string(memory_filepath)
    return graph.compile(checkpointer=memory)
