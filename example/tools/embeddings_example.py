# SPDX-License-Identifier: LGPL-3.0-or-later

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