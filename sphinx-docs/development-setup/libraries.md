# Library Dependencies & Their Roles in Maeser

*An at-a-glance guide to every major third-party library in Maeser: what it does, why it’s here, and how we leverage it.*

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
  - **Text splitters:** `RecursiveCharacterTextSplitter`  
  - **Embeddings:** `OpenAIEmbeddings`  
  - **Vector store wrapper:** `FAISS` integration  

### [FAISS (via LangChain)](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- **Role:** High-performance nearest-neighbor search  
- **Use case:** Index and query embedding vectors for both Simple and Pipeline RAG pipelines.

---

## Workflow Orchestration

### [LangGraph](https://langchain-ai.github.io/langgraph/?_gl=1*1a1ptos*_ga*MTA4OTcxNDQ3OS4xNzQ3NzUyMzU1*_ga_47WX3HKKY2*czE3NDc3NTIzNTQkbzEkZzEkdDE3NDc3NTIzNjgkajAkbDAkaDA.)
- **Role:** Compose multi-step AI pipelines as directed graphs
- **Use case:** Underpins `get_simple_rag` and `get_pipeline_rag`; foundation for advanced custom graphs.

---

## LLM & Embedding APIs

### [OpenAI Python SDK](https://platform.openai.com/docs/api-reference/introduction)
- **Role:** Official client for chat completions & embeddings
- **Use case:** Send prompts to GPT models (e.g., `gpt-3.5-turbo`, `gpt-4`) and retrieve embeddings when needed.

---

## 4. Web Framework & Templating

### [Flask](https://flask.palletsprojects.com/en/stable/quickstart/)
- **Role:** Lightweight WSGI framework for web endpoints
- **Use case:** Hosts chat UI, auth flows, admin dashboards—bootstrapped by `App_Manager`.

### [Jinja2](https://jinja.palletsprojects.com/en/stable/)
- **Role:** HTML templating engine
- **Use case:** Renders dynamic templates (chat interface, login, logs) with theming support.

---

## Configuration & Environment

### [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- **Role:** YAML parsing
- **Use case:** Load `config.yaml` (API keys, paths, rate limits, auth settings).

### [python-dotenv *(optional)*](https://www.dotenv.org/docs/)
- **Role:** `.env` support for environment variables
- **Use case:** Override sensitive settings outside of YAML or source control.

---

## Authentication & User Management

### [LDAP3](https://ldap3.readthedocs.io/en/latest/)
- **Role:** LDAP directory client
- **Use case:** `LDAPAuthenticator` for enterprise user login.

### [PyJWT](https://pyjwt.readthedocs.io/en/stable/)
- **Role:** JSON Web Token handling
- **Use case:** Sign and verify tokens for session security and rate limiting.

---

## CLI & Developer Tooling

### [pyinputplus](https://pyinputplus.readthedocs.io/en/latest/)
- **Role:** Enhanced `input()` for CLI menus & validation
- **Use case:** Powers the interactive terminal example.

### [pytest](https://docs.pytest.org/en/stable/contents.html)
- **Role:** Testing framework
- **Use case:** Runs unit tests under `tests/` to validate functionality.

### [Sphinx](https://www.sphinx-doc.org/en/master/) & [MyST Parser](https://myst-parser.readthedocs.io/en/latest/)
- **Role:** Documentation generator for RST & Markdown  
- **Use case:** Builds the Maeser docs site (`sphinx-docs/`) with mixed-format support.

---

## Optional Integrations

- **[Poetry](https://python-poetry.org/docs/):** Alternative dependency & venv management  
- **[Gunicorn](https://docs.gunicorn.org/en/stable/):** Production-ready WSGI server  
- **[Docker](https://docs.docker.com/get-started/):** Containerization for reproducible deployments

---

## Best Practices & Tips

- Keep **LangChain** and **OpenAI SDK** versions up-to-date.  
- Swap FAISS for another vector store (e.g., Chroma) by updating only pipeline construction.  
- Use **python-dotenv** in dev to keep secrets out of YAML/source.  
- Configure **pre-commit hooks** (Black, Flake8, isort) for consistent code style.

With this guide, you’ll quickly grasp each library’s purpose and role within Maeser’s architecture, making your customization and troubleshooting even easier.