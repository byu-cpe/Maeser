"""Module for creating a simple retrieval-augmented generation (RAG) graph using LangChain."""

from langchain_core.documents.base import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from typing_extensions import TypedDict
from typing import List, Annotated
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver

def get_simple_rag(
    vectorstore_path: str,
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
    """Create a simple retrieval-augmented generation (RAG) graph.
    
    Args:
        vectorstore_path (str): Path to the vector store.
        vectorstore_index (str): Index name for the vector store.
        memory_filepath (str): Filepath for the memory checkpoint.
        api_key (str | None): API key for the language model. Defaults to None.
        system_prompt_text (str): Prompt text for the system message. Defaults to a helpful teacher prompt.
        model (str): Model name for the language model. Defaults to 'gpt-4o-mini'.
    
    Returns:
        CompiledGraph: The compiled state graph.
    """

    def add_messages(left: list, right: list):
        """Add-don't-overwrite."""
        return left + right

    class GraphState(TypedDict):
        """Represents the state of the graph."""
        retrieved_context: List[Document]
        messages: Annotated[list, add_messages]

    llm: ChatOpenAI = ChatOpenAI(model=model) if api_key is None else ChatOpenAI(api_key=api_key, model=model)  # type: ignore

    retriever: VectorStoreRetriever = FAISS.load_local(
        vectorstore_path,
        OpenAIEmbeddings() if api_key is None else OpenAIEmbeddings(api_key=api_key),  # type: ignore
        allow_dangerous_deserialization=True,
        index_name=vectorstore_index,
    ).as_retriever()

    system_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages([
        ('system', system_prompt_text),
        MessagesPlaceholder('messages'),
        ('human', '{input}'),
    ])

    chain = system_prompt | llm | StrOutputParser()

    def retrieve_node(state: GraphState) -> dict:
        """Retrieve context documents based on the latest question."""
        question = state['messages'][-1]
        documents: List[Document] = retriever.invoke(question)
        return {'retrieved_context': documents}

    def generate_node(state: GraphState) -> dict:
        """Generate a response based on the context and messages."""
        messages = state['messages']
        documents: List[Document] = state['retrieved_context']
        generation: str = chain.invoke({
            'context': documents,
            'messages': messages[:-1],
            'input': messages[-1],
        })
        return {'messages': [generation]}

    graph = StateGraph(GraphState)

    graph.add_node('retrieve', retrieve_node)
    graph.add_node('generate', generate_node)
    graph.add_edge('retrieve', 'generate')
    graph.set_entry_point('retrieve')
    graph.set_finish_point('generate')

    memory = SqliteSaver.from_conn_string(f'{memory_filepath}')

    compiled_graph: CompiledGraph = graph.compile(checkpointer=memory)

    return compiled_graph
