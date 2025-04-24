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

## 1. Retrieval & Embeddings

### 1.1 LangChain
- **Role:** High-level RAG abstraction layer
- **Key features used:**
  - **Text splitters:** `RecursiveCharacterTextSplitter`  
  - **Embeddings:** `OpenAIEmbeddings`  
  - **Vector store wrapper:** `FAISS` integration  

### 1.2 FAISS (via LangChain)
- **Role:** High-performance nearest-neighbor search  
- **Use case:** Index and query embedding vectors for both Simple and Pipeline RAG pipelines.

---

## 2. Workflow Orchestration

### LangGraph
- **Role:** Compose multi-step AI pipelines as directed graphs
- **Use case:** Underpins `get_simple_rag` and `get_pipeline_rag`; foundation for advanced custom graphs.

---

## 3. LLM & Embedding APIs

### OpenAI Python SDK
- **Role:** Official client for chat completions & embeddings
- **Use case:** Send prompts to GPT models (e.g., `gpt-3.5-turbo`, `gpt-4`) and retrieve embeddings when needed.

---

## 4. Web Framework & Templating

### Flask
- **Role:** Lightweight WSGI framework for web endpoints
- **Use case:** Hosts chat UI, auth flows, admin dashboards—bootstrapped by `App_Manager`.

### Jinja2
- **Role:** HTML templating engine
- **Use case:** Renders dynamic templates (chat interface, login, logs) with theming support.

---

## 5. Configuration & Environment

### PyYAML
- **Role:** YAML parsing
- **Use case:** Load `config.yaml` (API keys, paths, rate limits, auth settings).

### python-dotenv *(optional)*
- **Role:** `.env` support for environment variables
- **Use case:** Override sensitive settings outside of YAML or source control.

---

## 6. Authentication & User Management

### LDAP3
- **Role:** LDAP directory client
- **Use case:** `LDAPAuthenticator` for enterprise user login.

### PyJWT
- **Role:** JSON Web Token handling
- **Use case:** Sign and verify tokens for session security and rate limiting.

---

## 7. CLI & Developer Tooling

### pyinputplus
- **Role:** Enhanced `input()` for CLI menus & validation
- **Use case:** Powers the interactive terminal example.

### pytest
- **Role:** Testing framework
- **Use case:** Runs unit tests under `tests/` to validate functionality.

### Sphinx & MyST Parser
- **Role:** Documentation generator for RST & Markdown  
- **Use case:** Builds the Maeser docs site (`sphinx-docs/`) with mixed-format support.

---

## 8. Optional Integrations

- **Poetry:** Alternative dependency & venv management  
- **Gunicorn:** Production-ready WSGI server  
- **Docker:** Containerization for reproducible deployments

---

## Best Practices & Tips

- Keep **LangChain** and **OpenAI SDK** versions up-to-date.  
- Swap FAISS for another vector store (e.g., Chroma) by updating only pipeline construction.  
- Use **python-dotenv** in dev to keep secrets out of YAML/source.  
- Configure **pre-commit hooks** (Black, Flake8, isort) for consistent code style.

With this guide, you’ll quickly grasp each library’s purpose and role within Maeser’s architecture, making your customization and troubleshooting even easier.