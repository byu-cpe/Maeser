# Embedding Content

Maeser currently works with locally saved FAISS vectorstores.

For complete information about creating vectorstores using LangChain, read [the docs](https://python.langchain.com/v0.1/docs/modules/data_connection/vectorstores/).

The example directory contains two scripts that show how an individual Wikipedia page could be vectorized: 
`create_byu_vectorstore.py` and `create_maeser_vectorstore`. 

The principles in these scripts could be applied to any content you would like to vectorize:
1) Preprocess the content and turn it into plaintext.
    ```python
    # Extract the text from the Karl G. Maeser Wikipedia page

    import wikipediaapi

    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='Maeser AI Example',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
    )

    p_wiki = wiki_wiki.page("Karl G. Maeser")
    text = p_wiki.text
    ```
2) Chunk the data strategically.
    ```python
    # Split the text into chunks

    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = text_splitter.create_documents([text])
    ```
3) Vectorize each chunk and save as FAISS database. 
    ```python
    # Save the vectorized text to a local FAISS vectorstore

    from langchain_community.vectorstores import FAISS

    db = FAISS.from_documents(documents, OpenAIEmbeddings())
    db.save_local("example/vectorstores/maeser")
    ```