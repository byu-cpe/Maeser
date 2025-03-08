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
from typing import List, Annotated, Dict, Tuple
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver

class GraphState (TypedDict):
    messages: List[str]
    current_topic: str | None = None
    retrieved_context: List[Document] | None = None

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
        vectorstore_config (Dict[str, Tuple[str, str]]): Mapping of topic to (vectorstore_path, index name)
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
        ('human', {input})
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
    def initial_topic_node(state: GraphState, vectorstore_config: Dict) -> dict:
        if not state.get("current_topic"):
            formated_topics = format_topic_keys(vectorstore_config)
            establish_topic = ChatPromptTemplate.from_messages([
                ('system', f"You are an assistant who extracts a concise topic label from a user's explanation. The label should be one of these topics {formated_topics}."),
                ('human', "User message: {question}\nCurrent topic: {current_topic}\nNew topic:")
            ])
            current_topic = state.get("current_topic") or "none"
            question = state["messages"][-1]
            formatted_prompt = establish_topic.format(question=question)
            llm_topic = ChatOpenAI(model=model, temperature=0) if api_key is None else ChatOpenAI(api_key=api_key, model=model, temperature=0)
            result = llm_topic.invoke([SystemMessage(content=formatted_prompt)])
            topic = result.content.strip().lower()
            return {"current_topic": topic}
        return {}
    