# Maeser Example (with Flask & User Management)

This guide demonstrates how to run Maeser as a web-based chatbot **with user authentication** (via GitHub OAuth or LDAP) using two example scripts--`flask_multigroup_example_user_management.py` and `flask_pipeline_example_user_management.py`. You’ll inspect the script, configure authentication, launch the server, and customize the application for your own RAG workflows.

> Note: If you want to get the example running without user authentication, follow this guide with `flask_multigroup_example.py` or `flask_pipeline_example.py` instead, skipping the User Manager setup.

---

## Prerequisites

- **Maeser development environment** set up (see [Development Setup](development_setup)).
- **Python 3.10+** virtual environment activated.
- **Configured Authentication** for your [GitHub app](#register-your-github-oauth-app), [LDAP server](#ldap-authentication-optional), or both. 
- **Pre-built FAISS vectorstores** at the paths referenced in `config_example.yaml`. The example scripts use the pre-built `byu` and `maeser` vectorstores found in `example/vectorstores`. See [Embedding New Content](embedding) for instructions on how to build and add your own vectorstores.

---

## Choosing Between Multigroup or Pipeline
`flask_multigroup_example_user_management.py` and `flask_pipeline_example_user_management.py` are very similar in their implementation but have a few key differences:

- **Multigroup** creates separate "branches" for each vectorstore, which configures the chatbot to use only one vectorstore per conversation.
- **Pipeline** adds all vectorstores to a single branch, which configures the chatbot to dynamically pull from any of the vectorstores based on the user's query.

Choose whichever example is more applicable to your needs. If you prefer each conversation thread to be focused on only one topic/vectorstore, use the **Multigroup** example. Otherwise, consider using the **Pipeline** example.

---

## Configuring `config_example.yaml`

Configure the following fields in your `config_example.yaml` file:

```yaml
### API keys are required for OpenAI and GitHub integrations ###
api_keys:
  openai_api_key: '<openai_api_key_here>'
  github_client_secret: '<github_client_secret>' # Only required if using Github Authentication


### Other application configurations ###

### Github Auth ###

github:
  github_client_id: '<github_client_id>'
  github_callback_uri: '<base_url>/login/github_callback'
  timeout: 10

### LDAP3 Auth ###

# Be sure to configure these values with the specifications of your LDAP3 server
# If you are not using an LDAP3 authentication option then these entries can be left blank
ldap3:
  name: '<ldap_name>'
  ldap_server_urls: ['<ldap_url_1>', '<ldap_url_2>', '<ldap_url_n>']
  ldap_base_dn: '<base_dn>'
  attribute_name: '<search_attribute>'
  search_filter: '({search_attribute}={search_value})'
  object_class: '<object_class_name>'
  attributes:
    - '<search_attribute>'
    - '<display_name_attribute>'
    - '<email_attribute>'
  ca_cert_path: '<ca_certificate_path>'
  connection_timeout: 10

### Configure the LLM and text embedding models ###

llm:
  llm_model_name: gpt-4o-mini
  llm_provider: openai
  token_limit: 400
```

**Field Descriptions**:
- **openai_api_key**: Key to authenticate with OpenAI’s API.
- **llm_** entries: Configuration for your LLM.
- **github_** entries: Configure GitHub OAuth flow.
- **ldap3_** entries: Configure LDAP authentication parameters.

> **Note:** Feel free to change other fields in `config_example.yaml` according to your needs (such as `vec_store_path` or `max_requests`)

---

## Inspect the Example Scripts
The following sections will go through `flask_multigroup_user_mangement_example.py` and `flask_pipeline_user_mangement_example.py` section by section and explain how the code works. Most of the code can be left unchanged and should work as-is assuming that `config_example.yaml` is configured correctly.

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
Defines system prompts that inject persona and context into the LLM. These differ between the pipeline and multigroup examples. Multigroup has prompts for each group, while pipeline has one prompt designed for the sum total of vector data.
```python
# Located in the "multigroup" example
maeser_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history based on the context provided.
    Don't answer questions about other things.

    {context}
    """

byu_prompt: str = """You are speaking about the history of Brigham Young University.
    You will answer a question about the history of BYU based on the context provided.
    Don't answer questions about other things.

    {context}
    """
```

```python
# Located in the "pipeline" example
pipeline_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    Don't answer questions about other things.

    {context}
"""
```

### RAG Graph Construction
Here we are creating RAG pipelines (Karl G. Maeser, BYU, and combined pipeline). These will be registered as separate chat branches in the web interface.
```python
# Multigroup
from maeser.graphs.simple_rag import get_simple_rag
from langgraph.graph.graph import CompiledGraph

maeser_simple_rag: CompiledGraph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/maeser", # Location of vectorstore
    vectorstore_index="index", # The name of your vectorstore's .faiss and .pkl files
    memory_filepath=f"{LOG_SOURCE_PATH}/maeser.db", # Location to store memory for this chatbot
    system_prompt_text=maeser_prompt, # The system instructions the chatbot should follow
    model=LLM_MODEL_NAME, # The name of the LLM model you are using
    )
sessions_manager.register_branch(branch_name="maeser", branch_label="Karl G. Maeser History", graph=maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/byu",
    vectorstore_index="index",
    memory_filepath=f"{LOG_SOURCE_PATH}/byu.db",
    system_prompt_text=byu_prompt,
    model=LLM_MODEL_NAME,
    )
sessions_manager.register_branch(branch_name="byu", branch_label="BYU History", graph=byu_simple_rag)

```

```python
# Pipeline
from maeser.graphs.simple_rag import get_simple_rag
from maeser.graphs.pipeline_rag import get_pipeline_rag
from langgraph.graph.graph import CompiledGraph

# Define vectorstores to be included in the pipeline RAG
vectorstore_config = {
    "byu history": f"{VEC_STORE_PATH}/byu",      # Vectorstore for BYU history.
    "karl g maeser": f"{VEC_STORE_PATH}/maeser"  # Vectorstore for Karl G. Maeser.
}

byu_maeser_pipeline_rag: CompiledGraph = get_pipeline_rag(
    vectorstore_config=vectorstore_config, # Vectorstores to include, as defined above
    memory_filepath=f"{LOG_SOURCE_PATH}/pipeline_memory.db", # Location to store memory for this chatbot
    system_prompt_text=(pipeline_prompt), # The system instructions the chatbot should follow
    model=LLM_MODEL_NAME) # The name of the LLM model you are using
sessions_manager.register_branch(branch_name="pipeline", branch_label="Pipeline", graph=byu_maeser_pipeline_rag)


```

---

## User Management Setup

### Configure Authenticators
Defines GitHub and LDAP authenticators for user login and request quotas. This is consistent across both examples. The code blocks for either LDAP or GitHub can be commented out if you are not planning to use its authentication.
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
Creates a `UserManager` instance and registers the authenticators. Only register both LDAP and GitHub if you are planning on integrating both authentication methods into your project.
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

Initializes the Flask app with both chat session and user managers, then registers all routes via [blueprints](../autodoc/maeser/maeser.blueprints).
```python
from flask import Flask

base_app = Flask(__name__)

from maeser.blueprints import App_Manager

# Create the App_Manager class

app_manager = App_Manager(
    app=base_app,
    app_name="Maeser Test App",
    flask_secret_key="secret",
    chat_session_manager=sessions_manager,
    user_manager=user_manager,
    chat_head="/static/Karl_G_Maeser.png"
)

# Initalize the flask blueprint
app: Flask = app_manager.add_flask_blueprint()

if __name__ == "__main__":
    app.run(port=3002)
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

1. In GitHub, click on your user profile and go to **Settings → Developer Settings → OAuth Apps → New OAuth App**.
2. Set **Homepage URL** to `http://localhost:3002` and **Authorization callback URL** to `http://localhost:3002/login/github_callback`.
3. Copy the **Client ID** and **Client Secret** into `config_example.yaml`.

---

## LDAP Authentication (Optional)

Ensure your LDAP server is reachable, and the fields in `config_example.yaml` match your directory’s schema. The `LDAPAuthenticator` will bind and lookup users based on these settings.

---

## Next Steps

- Follow the instruction in [Embedding New Content](embedding) to create your own vectorstores and add them to the example.
- Review the **CLI example** (`example/terminal_example.py`) for a terminal interface.
- Dive into **advanced workflows** in [Graphs: Simple RAG vs. Pipeline RAG](graphs).
- Study Maeser’s **architecture** in [Architecture Overview](architecture).

