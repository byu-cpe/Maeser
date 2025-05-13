# Maeser Example (with Flask & User Management)

This guide demonstrates how to run Maeser as a web-based chatbot **with user authentication** (via GitHub OAuth or LDAP) using two example scripts--"flask_multigroup_example_user_management.py" and "flask_pipeline_example_user_management.py". You’ll inspect the script, configure authentication, launch the server, and customize the application for your own RAG workflows.

---

## Prerequisites

- **Maeser development environment** set up (see `development_setup.md`).
- **Python 3.10+** virtual environment activated.
- **Maeser** installed in editable mode (`pip install -e .` or `make setup`).
- **Pre-built FAISS vectorstores** at the paths referenced in your config.

---

## Configuring `config.yaml`

Copy the example and update the following fields:

```yaml
# Path where chat logs and memory DBs are stored
LOG_SOURCE_PATH: "path/to/chat_logs"
# Your OpenAI API key for LLM access\ OPENAI_API_KEY: "your-openai-key"
# SQLite file path to store registered users and quotas
USERS_DB_PATH: "path/to/users.db"
# Directory containing FAISS vectorstore folders
VEC_STORE_PATH: "path/to/vectorstores"
# Path for chat history JSON or DB
CHAT_HISTORY_PATH: "path/to/chat_history"
# LLM model name (e.g., gpt-4o)
LLM_MODEL_NAME: "gpt-4o"
# Maximum requests per user and rate-limit interval (seconds)
MAX_REQUESTS: 100
RATE_LIMIT_INTERVAL: 60

# GitHub OAuth Configuration
GITHUB_CLIENT_ID: "your-client-id"
GITHUB_CLIENT_SECRET: "your-client-secret"
GITHUB_AUTH_CALLBACK_URI: "http://hostIP:3002/login/github_callback"
GITHUB_TIMEOUT: 10

# LDAP3 Authenticator Settings
LDAP3_NAME: "ldap"
LDAP_SERVER_URLS:
  - "ldap://ldap.example.com"
LDAP_BASE_DN: "dc=example,dc=com"
LDAP_ATTRIBUTE_NAME: "uid"
LDAP_SEARCH_FILTER: "(objectClass=person)"
LDAP_OBJECT_CLASS: "person"
LDAP_ATTRIBUTES:
  - "cn"
  - "mail"
LDAP_CA_CERT_PATH: "/path/to/ca_cert.pem"
LDAP_CONNECTION_TIMEOUT: 5
```

**Field Descriptions**:
- **LOG_SOURCE_PATH**: Directory/file prefix for RAG memory databases.
- **OPENAI_API_KEY**: Key to authenticate with OpenAI’s API.
- **USERS_DB_PATH**: SQLite DB for storing user records and quotas.
- **VEC_STORE_PATH**: Base path where FAISS indexes are saved.
- **CHAT_HISTORY_PATH**: Path to persist chat logs via `ChatLogsManager`.
- **LLM_MODEL_NAME**: Which OpenAI or LLM model to invoke.
- **MAX_REQUESTS / RATE_LIMIT_INTERVAL**: Controls per-user rate limiting.
- **GITHUB_** entries: Configure GitHub OAuth flow.
- **LDAP3_** entries: Configure LDAP authentication parameters.

---

## Inspect `flask_multigroup_user_mangement_example.py` and `flask_pipeline_user_mangement_example.py`

### Configuration Imports & Env Setup
Imports all config variables and sets the OpenAI API key in the environment.
```python
from config_example import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, USERS_DB_PATH,
    VEC_STORE_PATH, MAX_REQUESTS, RATE_LIMIT_INTERVAL,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
    GITHUB_AUTH_CALLBACK_URI, GITHUB_TIMEOUT,
    CHAT_HISTORY_PATH,
    LDAP3_NAME, LDAP_SERVER_URLS, LDAP_BASE_DN,
    LDAP_ATTRIBUTE_NAME, LDAP_SEARCH_FILTER,
    LDAP_OBJECT_CLASS, LDAP_ATTRIBUTES,
    LDAP_CA_CERT_PATH, LDAP_CONNECTION_TIMEOUT,
    LLM_MODEL_NAME
)
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
```

### Chat Logs & Session Manager Setup
Initializes chat logging and session management to track conversations and user queries.
```python
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

# Persist chat history
chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
# Manage multiple chat sessions
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)
```

### Prompt Definitions
Defines system prompts that inject persona and context into the LLM. These differ between the pipeline and multigroup RAGs. multigroup has promptsper group, while pipeline has one prompt designed for all data.
```python
#located in the "multigroup" example
maeser_prompt = (
    """You are speaking from the perspective of Karl G. Maeser.\n"
    "You will answer questions about your life history based on provided context.\n"
    "{context}"""
)

byu_prompt = (
    """You are a BYU historian.\n"
    "You will answer questions about Brigham Young University’s history based on provided context.\n"
    "{context}"""
)

```

```python
# located in the "pipeline" example
pipeline_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    Don't answer questions about other things.

    {context}
"""
```

### RAG Graph Construction
Here we are creating RAG pipelines (Karl Maeser, BYU, and combined pipeline) and register them as named branches.
```python
# Multigroup
from maeser.graphs.simple_rag import get_simple_rag
from langgraph.graph.graph import CompiledGraph

maeser_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path=f"{VEC_STORE_PATH}/maeser",
vectorstore_index="index", memory_filepath=f"{LOG_SOURCE_PATH}/maeser.db", system_prompt_text=maeser_prompt, model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="maeser", branch_label="Karl G. Maeser History", graph=maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path=f"{VEC_STORE_PATH}/byu", vectorstore_index="index", memory_filepath=f"{LOG_SOURCE_PATH}/byu.db", system_prompt_text=byu_prompt, model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="byu", branch_label="BYU History", graph=byu_simple_rag)

```


```python
# located in the "pipeline" example
pipeline_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    Don't answer questions about other things.

    {context}
"""
```

### RAG Graph Construction
Here we are creating RAG pipelines (Karl Maeser, BYU, and combined pipeline) and register them as named branches.
```python
# Pipeline
from maeser.graphs.simple_rag import get_simple_rag
from maeser.graphs.pipeline_rag import get_pipeline_rag
from langgraph.graph.graph import CompiledGraph

vectorstore_config = {
    "byu history": f"{VEC_STORE_PATH}/byu",      # Vectorstore for BYU history.
    "karl g maeser": f"{VEC_STORE_PATH}/maeser"  # Vectorstore for Karl G. Maeser.
}

byu_maeser_pipeline_rag: CompiledGraph = get_pipeline_rag(
    vectorstore_config=vectorstore_config, 
    memory_filepath=f"{LOG_SOURCE_PATH}/pipeline_memory.db",
    api_key=OPENAI_API_KEY, 
    system_prompt_text=(pipeline_prompt),
    model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="pipeline", branch_label="Pipeline", graph=byu_maeser_pipeline_rag)


```

---

## User Management Setup

### Configure Authenticators
Defines GitHub and LDAP authenticators for user login and request quotas. This is consistent across both examples.
```python
from maeser.user_manager import UserManager, GithubAuthenticator, LDAPAuthenticator

# GitHub OAuth setup
github_authenticator = GithubAuthenticator(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    auth_callback_uri=GITHUB_AUTH_CALLBACK_URI,
    timeout=GITHUB_TIMEOUT,
    max_requests=MAX_REQUESTS
)

# LDAP Authenticator setup
ldap3_authenticator = LDAPAuthenticator(
    name=LDAP3_NAME,
    ldap_server_urls=LDAP_SERVER_URLS,
    ldap_base_dn=LDAP_BASE_DN,
    attribute_name=LDAP_ATTRIBUTE_NAME,
    search_filter=LDAP_SEARCH_FILTER,
    object_class=LDAP_OBJECT_CLASS,
    attributes=LDAP_ATTRIBUTES,
    ca_cert_path=LDAP_CA_CERT_PATH,
    connection_timeout=LDAP_CONNECTION_TIMEOUT
)
```

### Initialize User Manager
Creates a `UserManager` instance and registers the authenticators.
```python
# Initialize user management with request limits
user_manager = UserManager(
    db_file_path=USERS_DB_PATH,
    max_requests=MAX_REQUESTS,
    rate_limit_interval=RATE_LIMIT_INTERVAL
)
# Register both authenticators
user_manager.register_authenticator(name="github", authenticator=github_authenticator)
user_manager.register_authenticator(name=LDAP3_NAME, authenticator=ldap3_authenticator)
```

---

## Flask Application Setup

Initializes the Flask app with both chat session and user managers, then registers all routes via blueprints.
```python
from flask import Flask
from maeser.blueprints import App_Manager

base_app = Flask(__name__)
app_manager = App_Manager(
    app=base_app,
    app_name="Maeser Auth Chat",
    flask_secret_key="secret",
    chat_session_manager=sessions_manager,
    user_manager=user_manager,
    chat_head="/static/Karl_G_Maeser.png"
)
# Mount routes and return the full app
app = app_manager.add_flask_blueprint()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002, debug=True)
```

---

## Run the Application

Activate your virtual environment and execute one of the following commands:
```bash
python example/flask_multigroup_user_mangement_example.py
python example/flask_pipeline_user_mangement_example.py
```
Navigate to **http://localhost:3002**, authenticate via GitHub or LDAP, select a branch, and start chatting.

---

## Register Your GitHub OAuth App

1. In GitHub, go to **Settings → Developer Settings → OAuth Apps → New OAuth App**.
2. Set **Homepage URL** to `http://localhost:3002` and **Authorization callback URL** to `http://localhost:3002/login/github_callback`.
3. Copy the **Client ID** and **Client Secret** into `config.yaml`.

---

## LDAP Authentication (Optional)

Ensure your LDAP server is reachable, and the fields in `config.yaml` match your directory’s schema. The `LDAPAuthenticator` will bind and lookup users based on these settings.

---

## Customization & Debugging

- **Prompts & Branches**: Modify prompt strings or register additional graphs via `sessions_manager.register_branch()`.
- **Templates**: Edit Jinja2 templates in `maeser/controllers/common/templates/` for UI changes.
- **Static Assets**: Override CSS/JS in `common/static/`.
- **Debug Mode**: `debug=True` enables auto-reload and detailed tracebacks.
- **Production**: Run with a WSGI server such as Gunicorn:
  ```bash
  gunicorn example.flask_example_user_mangement:app -b 0.0.0.0:3002
  ```

---

## Next Steps

- Review the **CLI example** (`example/terminal_example.py`) for a terminal interface.
- Dive into **advanced workflows** in `graphs.md`.
- Study Maeser’s **architecture** in `architecture.md` before contributing.

Enjoy your authenticated Maeser chatbot! 🚀

