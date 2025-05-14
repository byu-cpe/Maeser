import os

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

<<<<<<< HEAD

os.environ["OPENAI_API_KEY"] = ""
=======
# For my sanity's sake, I am having my key be read in from a local, unsunc file.
# This is also to make it easier and more secure to run from inside a container, by getting the key
# external to the container but encrypted, when implemented.
os.environ["OPENAI_API_KEY"] = str(open("Keys.txt").readline().strip())
>>>>>>> Local_Adam_Sandland

# Load and combine all text from .txt files in the "output" directory
# This will provide one unified file per upload for training data, try to make it separate data for separate sources later on?
texts = []
output_dir = "output"
for filename in os.listdir(output_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(output_dir, filename), "r", encoding="utf-8") as f:
            texts.append(f.read())

# Split all loaded texts into documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = text_splitter.create_documents(texts)

# Save the vectorized text to a local FAISS vectorstore
db = FAISS.from_documents(documents, OpenAIEmbeddings())
db.save_local("data_stores")
