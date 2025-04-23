# Embedding New Content

This guide explains how to embed your own documents into a Maeser-compatible vector store, enabling Retrieval‑Augmented Generation (RAG) over custom knowledge bases.

---

## Prerequisites

- A **Maeser development** or **user** environment set up (see `development_setup.md`).
- **Python 3.10+** virtual environment activated.
- **Maeser** and its dependencies installed (`pip install -e .` or `make setup`).
- Your documents in **plain text** format (e.g., `.txt`, Markdown `.md`, or PDF converted to text).

---

## 1. Prepare Your Text Data

1. Collect all source files you want to embed into a single folder (e.g., `docs/homework`, `docs/labs`, etc.).
2. If your files are not plain text (e.g., PDF), convert them first. A simple example using `pdftotext`:
   ```bash
   pdftotext input.pdf output.txt
   ```
3. Ensure each file’s encoding is UTF‑8 to avoid errors when reading in Python.

---

## 2. Chunk Your Documents

Large documents must be split into smaller, semantically meaningful chunks before embedding:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

# Read all text files
folder = Path("docs/my_knowledge")
docs = [f.read_text(encoding="utf8") for f in folder.glob("*.txt")]

# Configure splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

# Generate chunks
texts = []
for doc in docs:
    texts.extend(splitter.split_text(doc))
```

> **Tip:** Adjust `chunk_size` and `chunk_overlap` based on your document structure. Smaller chunks improve retrieval precision but increase vector store size.

---

## 3. Create the Vector Store

Use FAISS (via LangChain) to embed and store your chunks:

```python
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Build or load FAISS vector store
vectorstore = FAISS.from_texts(
    texts,
    embeddings,
    meta_data=[{"source": f.name} for f in folder.glob("*.txt")]
)

# Persist to disk
vectorstore.save_local("my_vectorstore")
```

- `my_vectorstore/` will contain index files you can reuse in Maeser.
- Metadata (`source` field) helps trace which document each vector originated from.

---

## 4. Integrate with Maeser

In your Maeser application (e.g., in `flask_example.py` or your custom script):

```python
from maeser.graphs.simple_rag import get_simple_rag
from maeser.chat.chat_session_manager import ChatSessionManager

# Instantiate session manager and logs
sessions = ChatSessionManager()

# Create a RAG graph pointing to your vector store
my_rag_graph = get_simple_rag(
    vectorstore_path="my_vectorstore",
    system_prompt_text="You are an expert on my documents.",
)

# Register it as a new branch
sessions.register_branch(
    name="custom",
    label="My Custom Knowledge",
    graph=my_rag_graph
)
```

Now, when you run the Maeser app, your new "My Custom Knowledge" branch will retrieve answers from your embedded content.

---

## 5. Additional Tips

- **Rebuilding embeddings:** Whenever you update your source documents, delete `my_vectorstore/` and rerun the vector store creation step.
- **Batch embeddings:** For large corpora, consider parallelizing embeddings or using `batch` parameter in `OpenAIEmbeddings`.
- **Alternative backends:** You can swap FAISS for other vector stores supported by LangChain (e.g., Chroma, Pinecone) by changing the import and API calls.

---

## Next Steps

- Explore **custom graph workflows** for advanced RAG pipelines (`graphs.md`).
- Learn to **fine‑tune system prompts** and session behavior in Maeser’s architecture overview (`architecture.md`).
- Contribute improvements or report issues on the Maeser GitHub repository.


