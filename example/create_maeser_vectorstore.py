"""
© 2024 Blaine Freestone

This file is part of the Maeser usage example.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""

# Extract the text from the Karl G. Maeser Wikipedia page

import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="Maeser AI Example",
    language="en",
    extract_format=wikipediaapi.ExtractFormat.WIKI,
)

p_wiki = wiki_wiki.page("Karl G. Maeser")
text = p_wiki.text

# Split the text into chunks

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = text_splitter.create_documents([text])

# Save the vectorized text to a local FAISS vectorstore

from langchain_community.vectorstores import FAISS

db = FAISS.from_documents(documents, OpenAIEmbeddings())
db.save_local("vectorstores/maeser")
