# After running this script, be sure to move `gmtk` to the vectorstores directory

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

def format_name(filename:str):
    """Formats document names nicely.

    Args:
        filename (str): The name of the file. Assumed to be of the format "1_Name_of_Video.txt"

    Returns:
        str: Formatted document name
    """
    doc_name:str = filename.strip(".txt") # remove file extension
    doc_words:list = doc_name.split("_")[1:] # Gets words, removing document number before the first underscore
    doc_name = " ".join(doc_words) # Updates doc_name with the words in the title, separating them with spaces
    return doc_name

# Configure text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

# Read all text files and generate chunks
texts = [] # this is where the text chunks will be stored
metadatas = [] # this will keep track of which text chunks belong to which text file
folder = Path("transcripts")
for f in folder.glob("*.txt"):
    doc_raw = f.read_text(encoding="utf8")
    url, doc = doc_raw.split('\n', 1)
    chunks = splitter.split_text(doc)
    texts.extend(chunks) # store text chunks in texts
    doc_name:str = format_name(f.name) # Formats doc name nicely
    # print(doc_name)
    metadata = {
        "source_title": doc_name, # store video title in metadata
        "source_url": url, # store video url in metadata
    }
    metadatas.extend([metadata] * len(chunks)) # duplicate metadata so it corresponds with each text chunk

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

# print(texts)
# print(metadatas)

# Persist to disk
vectorstore.save_local("gmtk")