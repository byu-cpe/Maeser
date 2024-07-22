# Extract the text from the Karl G. Maeser Wikipedia page

import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='Maeser AI Example',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
)

p_wiki = wiki_wiki.page("Karl G. Maeser")
text = p_wiki.text

# Split the text into chunks and vectorize them

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = text_splitter.create_documents([text])

# Save the vectorized text to a local FAISS vectorstore

from langchain_community.vectorstores import FAISS

db = FAISS.from_documents(documents, OpenAIEmbeddings())
db.save_local("example/vectorstores/maeser")