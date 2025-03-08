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
from langgraph.graph.graph import CompiledGraph
from typing_extensions import TypedDict
from typing import List, Annotated
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver

def get_pipeline_rag (
    vectorstore_paths: list[str],
    vectorstore_index: str,
    memory_filepath: str,
    api_key: str | None = None,
    system_prompt_text: str = (
        'You are a helpful teacher helping a student with course material.\n'
        'Answer the question based on the provided course content:\n\n'
        '{context}\n'
    ),
    model: str = 'gpt-4o-mini'
) -> CompiledGraph:
    """Create a pipeline/dynamic retrieval-augmented generation (RAG) graph.
    
    Args:
        vectorstore_paths (): List of Paths to used vectorstores.
        vectorstore_index (str): Index name for the vector store.
        memory_filepath (str): Filepath for the memory checkpoint.
        api_key (str | None): API key for the language model. Defaults to None.
        system_prompt_text (str): Prompt text for the system message. Defaults to a helpful teacher prompt.
        model (str): Model name for the language model. Defaults to 'gpt-4o-mini'.
    
    Returns:
        CompiledGraph: The compiled state graph.
    """