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

def get_simple_rag(vectorstore_path: str, vectorstore_index: str, memory_filepath: str, api_key: str | None = None) -> CompiledGraph:
    def add_messages(left: list, right: list):
        """Add-don't-overwrite."""
        return left + right
    
    class GraphState(TypedDict):
        """Represents the state of the graph."""
        retrieved_context: List[str]
        messages: Annotated[list, add_messages]
    
    llm: ChatOpenAI = ChatOpenAI() if api_key is None else ChatOpenAI(api_key=api_key) # type: ignore

    retriever: VectorStoreRetriever = FAISS.load_local(
        vectorstore_path, 
        OpenAIEmbeddings() if api_key is None else OpenAIEmbeddings(api_key=api_key), # type: ignore
        allow_dangerous_deserialization=True, 
        index_name=vectorstore_index
    ).as_retriever()
    
    system_prompt_text: str = """You are a helpful teacher helping a student with course material.
    Answer the question based on the provided course content:

    {context}
    """
    system_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_text),
            MessagesPlaceholder("messages"),
            ("human", "{input}"),
        ]
    )
    
    chain = system_prompt | llm | StrOutputParser()

    def retrieve_node(state: GraphState) -> dict:
        question = state["messages"][-1]
        documents: List[Document] = retriever.invoke(question)
        return {"retrieved_context": documents}
    
    def generate_node(state) -> dict:
        messages = state["messages"]
        documents: List[Document] = state['retrieved_context']
        generation: str = chain.invoke({"context": documents, "messages": messages[:-1], "input": messages[-1]})
        return {"messages": [generation]}
    
    graph = StateGraph(GraphState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_edge("retrieve", "generate")
    graph.set_entry_point("retrieve")
    graph.set_finish_point("generate")

    memory = SqliteSaver.from_conn_string(f"{memory_filepath}")

    compiled_graph: CompiledGraph = graph.compile(checkpointer=memory)

    return compiled_graph