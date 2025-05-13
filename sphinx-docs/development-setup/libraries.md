# Library Dependencies & Their Roles in Maeser

An at-a-glance guide to every major third-party library in Maeser: what it does, why it’s here, and how we leverage it.

---

## Overview

Maeser weaves together best-in-class Python libraries to handle:  
- **Vector search & embeddings**  
- **Workflow orchestration**  
- **LLM API access**  
- **Web serving & templating**  
- **Authentication & configuration**  
- **CLI & developer tooling**

Understanding these dependencies empowers you to extend Maeser, debug quickly, and swap components as needed.

---

## Retrieval & Embeddings

### [LangChain](https://python.langchain.com/docs/introduction/)
- **Role:** High-level RAG abstraction layer
- **Key features used:**
  - **Text splitters:** [`RecursiveCharacterTextSplitter`](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html#langchain_text_splitters.character.RecursiveCharacterTextSplitter)  
  - **Embeddings:** [`OpenAIEmbeddings`](https://python.langchain.com/api_reference/openai/embeddings/langchain_openai.embeddings.base.OpenAIEmbeddings.html)  
  - **Vector store wrapper:** `FAISS` integration  

### [FAISS (via LangChain)](https://python.langchain.com/api_reference/community/vectorstores/langchain_community.vectorstores.faiss.FAISS.html)
- **Role:** High-performance nearest-neighbor search  
- **Use case:** Index and query embedding vectors for both Simple and Pipeline RAG pipelines.

---

## Workflow Orchestration

### [LangGraph](https://langchain-ai.github.io/langgraph/)
- **Role:** Compose multi-step AI pipelines as directed graphs
- **Use case:** Underpins `get_simple_rag` and `get_pipeline_rag`; foundation for advanced custom graphs.

---

## LLM & Embedding APIs

### [OpenAI Python SDK](https://github.com/openai/openai-python)
- **Role:** Official client for chat completions & embeddings
- **Use case:** Send prompts to GPT models (e.g., `gpt-3.5-turbo`, `gpt-4`) and retrieve embeddings when needed.

---

## 4. Web Framework & Templating

### [Flask](https://flask.palletsprojects.com/en/stable/)
- **Role:** Lightweight WSGI framework for web endpoints
- **Use case:** Hosts chat UI, auth flows, admin dashboards—bootstrapped by `App_Manager`.

### [Jinja2](https://jinja.palletsprojects.com/en/stable/)
- **Role:** HTML templating engine
- **Use case:** Renders dynamic templates (chat interface, login, logs) with theming support.

---

## Configuration & Environment

### [PyYAML](https://pypi.org/project/PyYAML/)
- **Role:** YAML parsing
- **Use case:** Load `config_example.yaml` (API keys, paths, rate limits, auth settings).

---

## Authentication & User Management

### Github OAth (Handled in [`user_manager`](../autodoc/maeser/maeser.user_manager))
- **Role:** Support for Github login.
- **Use case:** Provide users with the option to sign into the web application with github.

### [LDAP3](https://ldap3.readthedocs.io/en/latest/) (Handled in [`user_manager`](../autodoc/maeser/maeser.user_manager))
- **Role:** LDAP directory client
- **Use case:** `LDAPAuthenticator` for enterprise user login.

---

## CLI & Developer Tooling

### [pyinputplus](https://pypi.org/project/PyInputPlus/)
- **Role:** Enhanced input for CLI menus & validation
- **Use case:** Powers the interactive terminal example.

### [pytest](https://docs.pytest.org/en/stable/)
- **Role:** Testing framework
- **Use case:** Runs unit tests under `tests/` to validate functionality.

### [Sphinx](https://www.sphinx-doc.org/en/master/) & [MyST Parser](https://myst-parser.readthedocs.io/en/v0.16.1/sphinx/intro.html)
- **Role:** Documentation generator for RST & Markdown  
- **Use case:** Builds the Maeser docs site (`sphinx-docs/`) with mixed-format support.

---

## Optional Integrations

- **[Poetry:](https://python-poetry.org/)** Alternative dependency & venv management
- **[Gunicorn:](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/)** Production-ready WSGI server
- **[Docker:](https://docs.docker.com/)** Containerization for reproducible deployments

---