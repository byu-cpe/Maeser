# doc_chunker_operator.py
<<<<<<< HEAD
from langchain.text_splitter import RecursiveCharacterTextSplitter
=======
from langchain_text_splitters import RecursiveCharacterTextSplitter
>>>>>>> Local_Adam_Sandland
from pathlib import Path

# Read all text files
folder = Path("output")
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

# Save for import
if __name__ == "__main__":
    print(f"Generated {len(texts)} chunks.")
