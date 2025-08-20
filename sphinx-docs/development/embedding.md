# Embedding New Content

In order for the Maeser chatbot to use your documents, they must first be converted to a **vector store**. Each vector store is a directory containing an `index.faiss` and an `index.pkl` file. When you embed your documents as a vector store, the chatbot is able to pull relevant excerpts from the documents to aid its interactions with its users.

This guide explains how to use a Python script to embed your own documents into a vector store, enabling Retrieval‑Augmented Generation (RAG) over custom knowledge bases.

> **Note:** You can also use the [**Admin Portal**](../user-setup/admin_portal.md) to create vector stores without any coding required.

---

## Prerequisites

- A **Maeser development** or **user** environment set up (see [**Development Setup**](./development_setup.md)).
- Your documents in **plain text** format (e.g., `.txt`, Markdown `.md`, or PDF converted to text).

---

## Prepare Your Text Documents

1. Collect all source files you want to embed into a single folder (e.g., `docs/homework`, `docs/labs`, etc.).
2. If your files are not plain text (e.g., PDF), convert them first. A simple example using `pdftotext` on Linux:

   ```bash
   pdftotext input.pdf output.txt
   ```

3. Ensure each file’s encoding is UTF‑8 to avoid errors when reading in Python.

---

## Embed Your Documents into a New Vector Store

This guide will walk you through building your own python script for storing your data into vector stores. This code mirrors `embeddings_example.py` in the `example/tools/` directory. Feel free to use that code as a basis and modify it to your liking.

> **Note:** The `example/tools/` directory also contains the scripts `create_byu_vectorstore.py` and `create_maeser_vectorstore.py`. These scripts were used to create the example `byu` and `maeser` vector stores and can be a helpful reference to creating your own vector store script.

Your script for storing data will consist of two parts:

- **Chunking the documents** into smaller segments.
- **Storing the chunks** in FAISS vector store format.

### Chunk Your Documents

Large documents must be split into smaller, semantically meaningful chunks before embedding:

```python
DOCS_PATH = "path/to/docs" # Path to the files you want to embed
DOCS_TYPE = "txt" # Type of documents to embed, e.g. "txt" or "md"

### Chunk the documents ###

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import os

# Configure text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

# Read all text files and generate chunks
texts = [] # this is where the text chunks will be stored
metadatas = [] # this will keep track of which text chunks belong to which text file
folder = Path(DOCS_PATH)
for f in folder.glob(f"*.{DOCS_TYPE}"):
    doc = f.read_text(encoding="utf8")
    doc_name = os.path.splitext(f.name)[0]  # Get the file name without extension
    chunks = splitter.split_text(doc)
    texts.extend(chunks) # store text chunks in texts
    metadatas.extend([{"source": doc_name}] * len(chunks)) # store document name in metadatas
```

> **Tip:** Adjust `chunk_size` and `chunk_overlap` based on your document structure. Smaller chunks improve retrieval precision but increase vector store size.

---

### Store the Chunked Document as a FAISS Vector Store

Use **FAISS** (via **LangChain**) to embed and store your chunks:

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

- `my_vectorstore/` will contain index files (`index.faiss` and `index.pkl`) that you can reuse in Maeser.
- Metadatas (`source` field) helps trace which document each vector store chunk originated from. This information will be passed to your chatbot when retrieving context from your vector store.

> **Tip:** The code above assumes the **OPENAI_API_KEY environment variable** is defined like so:
>
> ```bash
> # Linux and Mac
> $ export OPENAI_API_KEY="<your_api_key_here>"
> ```
>
> ```powershell
> # Windows (Powershell)
> > $Env:OPENAI_API_KEY = "<your_api_key_here>"
> ```
>
> If you instead want to pass your api key into the script **without using the environment variable**, assign it when initializing your embeddings:
>
> ```python
> embeddings = OpenAIEmbeddings(api_key="<your_api_key_here>")
> ```

---

## Integrate with Maeser

Now that you have created a new vector store for your documents, you must configure your chatbot to use this vector store when generating a response. To do this you'll need to:

1. Write a system prompt for your chatbot to follow
2. Initialize a RAG graph with your vector store
3. Register the system prompt and RAG graph to a new chat branch

If you are using one of the **Simple RAG** scripts in `example/apps/simple/`, add  this to your flask script:

```python
# Add rules in my_prompt for your chatbot to follow. Example:
my_prompt: str = """You are a helpful professor.
    You will answer students' questions based on the context provided.
    If the question is unrelated to the context, politely inform the user that their question is outside the context of your resources.

    {context}
    """

# Initialize the Simple RAG graph
my_simple_rag: CompiledGraph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/my_vectorstore",
    vectorstore_index="index",
    memory_filepath=f"{LOG_SOURCE_PATH}/my_course.db",
    api_key=OPENAI_API_KEY,
    system_prompt_text=my_prompt,
    model=LLM_MODEL_NAME,
)

# Register the system prompt and RAG graph to a new chat branch
sessions_manager.register_branch(branch_name="my_course", branch_label="My Course", graph=my_simple_rag)
```

If you are using one of the  **Universal RAG** or **Pipeline RAG** scripts, add  this to your flask script:

```python
# NOTE: universal_prompt, vectorstore_config, and my_universal_rag already exist in your flask script and only need to be altered

# Add rules in universal_prompt for your chatbot to follow. Example:
universal_prompt: str = """You are a helpful professor.
    You will answer students' questions based on the context provided.
    If the question is unrelated to the context, politely inform the user that their question is outside the context of your resources.

    {context}
    """

# Add your vector store to vectorstore_config
# Ensure that topics are all lower case and spaces between words
vectorstore_config = {
    # -- Other vector stores listed here -- #
    "my course": f"{VEC_STORE_PATH}/my_vectorstore", # Path to your vector store
}

# Register your RAG Graph and chat branch
my_universal_rag: CompiledGraph = get_universal_rag(
    vectorstore_config=vectorstore_config,
    memory_filepath=f"{LOG_SOURCE_PATH}/my_course.db",
    api_key=OPENAI_API_KEY,
    system_prompt_text=universal_prompt,
    model=LLM_MODEL_NAME,
)

sessions_manager.register_branch(branch_name="my_course", branch_label="My Course", graph=my_universal_rag)
```

---

## Additional Tips

- **Rebuilding embeddings:** Whenever you update your source documents, delete `my_vectorstore/` and rerun the vector store creation step.

---

## Next Steps

- Review the **example Flask scripts** in [**Maeser Example (with Flask & User Management)**](flask_example).
- Explore **custom graph workflows** for advanced RAG pipelines in [**Graphs**](./graphs.md).
- Prepare your custom Maeser application for [**server deployment**](../sysadmin/deployment.md).
