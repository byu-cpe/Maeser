# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module is used to vectorize data from text files.
Output files will be saved in **output_dir** as "index.faiss" and "index.pkl".
This module can be executed in the terminal or used within another script.
"""

import os
import sys

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from maeser.config import OPENAI_API_KEY as key

os.environ["OPENAI_API_KEY"] = key # Modify this line to open it from a cloud based file


# Load and combine all text from .txt files in the "output" directory
# This will provide one unified file per upload for training data, try to make it separate data for separate sources later on?
def vectorize_data(output_dir: str):
    """Vectorizes text files in **output_dir** and saves the resultant files as "index.faiss" and "index.pkl".

    Args:
        output_dir (str): The directory where the text files are located and where the vectorstore will be saved.
    """

    # Read in all texts
    texts = []
    metadatas = []
    for filename in os.listdir(output_dir):
        if filename.endswith(".md"):
            source_name = os.path.splitext(filename)[0].replace("_", " ")
            with open(os.path.join(output_dir, filename), "r", encoding="utf-8") as f:
                texts.append(f.read())
                metadatas.append({"source": source_name})

    # Split all loaded texts into documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = text_splitter.create_documents(
        texts=texts,
        metadatas=metadatas,
    )

    # Save the vectorized text to a local FAISS vector store
    db = FAISS.from_documents(documents, OpenAIEmbeddings())
    db.save_local(output_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python vector_store_operator.py <directory>")
        sys.exit(1)
    output_dir = sys.argv[1]
    vectorize_data(output_dir)
    