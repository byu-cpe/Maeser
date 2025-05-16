# Embedding New Content

This guide explains how to embed your own documents into a Maeser-compatible vector store, enabling Retrieval‑Augmented Generation (RAG) over custom knowledge bases.

---

## Prerequisites

- A **Maeser development** or **user** environment set up (see [Development Setup](development_setup)).
- **Python 3.10+** virtual environment activated.
- **Maeser** and its dependencies installed (`pip install -e .` or `make setup`).
- Your documents in **plain text** format (e.g., `.txt`, Markdown `.md`, or PDF converted to text).

---

## Prepare Your Text Data

1. Collect all source files you want to embed into a single folder (e.g., `docs/homework`, `docs/labs`, etc.).
2. If your files are not plain text (e.g., PDF), convert them first. A simple example using `pdftotext`:
   ```bash
   pdftotext input.pdf output.txt
   ```
3. Ensure each file’s encoding is UTF‑8 to avoid errors when reading in Python.

---

## Chunk Your Documents

Large documents must be split into smaller, semantically meaningful chunks before embedding:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

# Configure text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

# Read all text files and generate chunks
texts = [] # this is where the text chunks will be stored
metadatas = [] # this will keep track of which text chunks belong to which text file
folder = Path("path/to/txts")
for f in folder.glob("*.txt"):
    doc = f.read_text(encoding="utf8")
    chunks = splitter.split_text(doc)
    texts.extend(chunks) # store text chunks in texts
    metadatas.extend([{"source": f.name}] * len(chunks)) # store file name in metadatas
```

> **Tip:** Adjust `chunk_size` and `chunk_overlap` based on your document structure. Smaller chunks improve retrieval precision but increase vector store size.

---

## Create the Vector Store

Use FAISS (via LangChain) to embed and store your chunks:

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Build or load FAISS vector store
vectorstore = FAISS.from_texts(
    texts,
    embeddings,
    metadatas
)

# Persist to disk
vectorstore.save_local("my_vectorstore")
```

- `my_vectorstore/` will contain index files you can reuse in Maeser.
- Metadatas (`source` field) helps trace which document each vector originated from.

> **Tip:** The code above assumes the OPENAI_API_KEY environment variable is defined. If you want to pass your api key into the script without using the environment variable, assign it when initializing your embeddings:
> ```
> embeddings = OpenAIEmbeddings(api_key=<your_api_key_here>)
> ```

---

## Integrate with Maeser

The following code snippet assumes that you have an initialized `ChatSessionManager` object called `sessions_manager` and that you have imported config variables from `config_example.py`. Add the following code to your Maeser application (e.g., in `flask_example.py` or your custom script):

```python
from maeser.graphs.simple_rag import get_simple_rag
from langgraph.graph.graph import CompiledGraph

# Create a system prompt for your chatbot with appended context. Example prompt:
my_prompt: str = """
    You are a helpful teacher helping a student with course material.
    You will answer a question based on the context provided.
    Don't answer questions about other things.

    {context}
"""

# Create a RAG graph pointing to your vector store
my_simple_rag: CompiledGraph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/my_vectorstore",
    vectorstore_index="index", # the name of the .faiss and .pkl files in your vectorstore
    memory_filepath=f"{LOG_SOURCE_PATH}/my_branch.db",
    system_prompt_text=my_prompt,
    model=LLM_MODEL_NAME
)
# Register it as a new branch
sessions_manager.register_branch(
    branch_name="my_branch",
    branch_label="My Custom Knowledge",
    graph=my_simple_rag,    
)
```

Now, when you run the Maeser app, your new "My Custom Knowledge" branch will retrieve answers from your embedded content.

---

## Additional Tips

- **Rebuilding embeddings:** Whenever you update your source documents, delete `my_vectorstore/` and rerun the vector store creation step.
- **Batch embeddings:** For large corpora, consider parallelizing embeddings or using `batch` parameter in `OpenAIEmbeddings`.
- **Alternative backends:** You can swap FAISS for other vector stores supported by LangChain (e.g., Chroma, Pinecone) by changing the import and API calls.

---

## Next Steps

- Explore **custom graph workflows** for advanced RAG pipelines in [Graphs: Simple RAG vs. Pipeline RAG](graphs).
- Review the **example flask scripts** in [Maeser Example (with Flask & User Management)](flask_example).


