# Maeser Example (with Flask & User Management)

There are several example scripts found in `example/apps/` that you can use to make your own Maeser application. The scripts are organized into subdirectories based on chatbot behavior:

- **`simple/`** contains scripts that separate each vectorstore into its own branch, forcing the chatbot to stick to one topic per conversation.
- **`pipeline/`** contains scripts that combine all vectorstores into one chat branch, allowing the chatbot to dynamically choose the most relevant vectorstore when answering a user's question.
- **`universal/`** contains scripts that combine all vectorstores into one chat branch, like the `pipeline/` scripts, but also allow the chatbot to pull from multiple vectorstores when answering a user's question.

> **Note:** For more details on how these work, see [**Graphs**](./graphs.md).

Each subdirectory contains the following implementations of Maeser:

- **flask_\*.py** implements Maeser as a Flask web application *without* user management.
- **flask_\*_user_management.py** implements Maeser as a Flask web application *with* user management.
- **terminal_*.py** implements Maeser as a terminal application.

This guide demonstrates how to run Maeser as a web-based chatbot **with user authentication** (via GitHub OAuth or LDAP) using the example script `universal/flask_universal_user_management.py`.

> **Note:** The steps in this guide can be applied to all the example scripts. Simply skip the user management steps if your example script does not include it.

---

## Prerequisites

- **Maeser development environment** (see [**Development Setup**](development_setup)).
- **Configured Authentication** for your [**GitHub app**](#register-your-github-oauth-app), [**LDAP server**](#register-your-ldap-authenticator-optional), or both.
- **Pre-built FAISS vectorstores** at the paths referenced in your `config.yaml` file. The example scripts use the pre-built `byu` and `maeser` vectorstores found in `example/resources/vectorstores`. See [**Embedding New Content**](embedding) for instructions on how to build and add your own vectorstores.

---

## Configuring `config.yaml`

Be sure to do the following if you have not already done so:

- **Make a copy of `example/apps/config_template.yaml`** and name it `config.yaml`.
- **Configure authentication for your authentication method**; either GitHub, LDAP, or both. For instructions on setting up these authenticators, see [**Configuring Authenticators**](#configuring-authenticators) on this page.

Configure the following fields in your `config.yaml` file:

```{code-block} yaml
:class: no-copybutton
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
- **github_** entries: Configure GitHub OAuth parameters.
- **ldap3_** entries: Configure LDAP authentication parameters.

> **Note:** Feel free to change other fields in `config.yaml` according to your needs (such as `vec_store_path` or `max_requests`).

---

## Inspect the Example Scripts

The following sections will go through `universal/flask_universal_user_management.py` section-by-section and explain how the code works. Most of the code can be left unchanged and should work as-is assuming that your `config.yaml` file is configured correctly. If your are using a different example script, pay attention to the notes below explaining any differences.

### Configuration Imports & Environment Setup

Imports all config variables and sets the OpenAI API key in the environment.

```python
from example.apps.config import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, USERS_DB_PATH, 
    VEC_STORE_PATH, MAX_REQUESTS, RATE_LIMIT_INTERVAL, 
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_AUTH_CALLBACK_URI, 
    GITHUB_TIMEOUT, CHAT_HISTORY_PATH, LDAP3_NAME, 
    LDAP_SERVER_URLS, LDAP_BASE_DN, LDAP_ATTRIBUTE_NAME, LDAP_SEARCH_FILTER, 
    LDAP_OBJECT_CLASS, LDAP_ATTRIBUTES, LDAP_CA_CERT_PATH, LDAP_CONNECTION_TIMEOUT, 
    LLM_MODEL_NAME, STATIC_FOLDER,
)

import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
```

### Chat Logs & Session Manager Setup

Initializes **chat log management** and **session management** to track conversations and user queries.

```python
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)
```

### Prompt Definitions

Defines system prompts that give the LLM its rules and personality.

```python
# The prompt for a Universal RAG is a generalized prompt, often for providing answers across larger datasets,
# but still specific to relevant course information.
universal_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    If the question is unrelated to the topic or the context, politely inform the user that their question is outside the context of your resources.
    
    {context}
"""
```

> **Note:** The scripts in the `simple/` subdirectory have one prompt for each vectorstore, whereas the scripts in `universal/` and `pipeline/` share one prompt across all vectorstores.

### RAG Graph Construction

Creates a **Retrieval Augmented Generation (RAG) graph** for the chatbot to follow and registers the graph with the sessions manager.

```python
from maeser.graphs.universal_rag import get_universal_rag
from langgraph.graph.graph import CompiledGraph

# One for the history of BYU and one for the life of Karl G. Maeser.
# Ensure that topics are all lower case and spaces between words
vectorstore_config = {
    "byu history": f"{VEC_STORE_PATH}/byu",      # Vectorstore for BYU history.
    "karl g maeser": f"{VEC_STORE_PATH}/maeser"  # Vectorstore for Karl G. Maeser.
}

byu_maeser_universal_rag: CompiledGraph = get_universal_rag(
    vectorstore_config=vectorstore_config,
    memory_filepath=f"{LOG_SOURCE_PATH}/universal_memory.db",
    api_key=OPENAI_API_KEY,
    system_prompt_text=(universal_prompt),
    model=LLM_MODEL_NAME,
)

# Register the branch with the Sessions Manager
sessions_manager.register_branch(branch_name="universal", branch_label="BYU and Karl G. Maeser History", graph=byu_maeser_universal_rag)
```

> **Note:** The scripts in the `simple/` subdirectory create and register one RAG graph for each individual vectorstore, whereas the scripts in `universal/` and `pipeline/` create one branch that accesses all vectorstores.

---

## User Management Setup

If you are using one of the example scripts that does not use user management, then this section may be skipped.

### Initialize Authenticators

Defines GitHub and LDAP authenticators for user login and request quotas. This is consistent across all `flask_*_user_management.py` scripts. The code blocks for either LDAP or GitHub can be commented out if you are not planning to use it as an authenticator.

```python
om maeser.user_manager import UserManager, GithubAuthenticator, LDAPAuthenticator

# Replace the '...' in the config_example.yaml with a client id and secret from a GitHub OAuth App that you generate
github_authenticator = GithubAuthenticator(
    client_id=GITHUB_CLIENT_ID, 
    client_secret=GITHUB_CLIENT_SECRET, 
    auth_callback_uri=GITHUB_AUTH_CALLBACK_URI,
    timeout=GITHUB_TIMEOUT,
    max_requests=MAX_REQUESTS
)

# Replace the '...' in the config_example.yaml with all the proper configurations
# If you are not using LDAP, comment out this block
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
    rate_limit_interval=RATE_LIMIT_INTERVAL,
)
user_manager.register_authenticator(name="github", authenticator=github_authenticator)
user_manager.register_authenticator(name=LDAP3_NAME, authenticator=ldap3_authenticator) # If you are not using LDAP, comment out this line
```

---

## Flask Application Setup

**Initializes the Flask app** with both chat session and user managers, then registers all routes via [**Maeser's Flask Blueprints**](../autodoc/maeser/maeser.blueprints.rst).

```python
from flask import Flask

# Default resources must be relative to the directory the Flask script is located in (regardless of current working directory)
app_dir = os.path.dirname(__file__)

# Configure base app
base_app = Flask(
    __name__,
    static_folder=os.path.relpath(STATIC_FOLDER, app_dir),
)

from maeser.blueprints import AppManager

# Create the AppManager class
app_manager = AppManager(
    app=base_app,
    app_name="Maeser Test App",
    flask_secret_key="secret",
    chat_session_manager=sessions_manager,
    user_manager=user_manager,
    chat_head="/static/Karl_G_Maeser.png"
)

# Initialize the flask blueprint
app: Flask = app_manager.add_flask_blueprint()

if __name__ == "__main__":
    app.run(port=3002)
```

---

## Enable Debug Mode (Optional)

When a Flask app is run in debug mode, it automatically reloads any time the Flask script or other scripts used by the app are changed. This mode can be helpful when you are debugging your Flask script or making changes. You can enable it in your script's `app.run()` call:

```python
if __name__ == "__main__":
    app.run(port=3002, debug=True)
```

---

## Run the Application

Activate your virtual environment and run your Flask script from the project root. Your terminal output should be similar to the following:

```bash
$ python example/apps/universal/flask_universal.py 
Using configuration at example/apps/config.yaml (Priority 0)
 * Serving Flask app 'flask_universal'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:3002
Press CTRL+C to quit
```

Navigate to `http://localhost:3002`, authenticate via GitHub or LDAP, select a branch, and start chatting.

---

## Configuring Authenticators

The following sections briefly outline how to configure your authenticator of choice with Maeser.

### Register Your GitHub OAuth App

1. In GitHub, click on your user profile and go to **Settings → Developer Settings → OAuth Apps → New OAuth App**.
2. Set **Homepage URL** to `http://localhost:3002` and **Authorization callback URL** to `http://localhost:3002/login/github_callback`.
3. Copy the **Client ID** and **Client Secret** into `config.yaml`.

---

### Register your LDAP Authenticator (Optional)

The configuration process for an LDAP Authenticator will vary depending on the authenticator used. Ensure your LDAP server is reachable, and the fields in `config.yaml` match your directory’s schema. The `LDAPAuthenticator` will bind and look up users based on these settings.

---

## Next Steps

- Follow the instruction in [**Embedding New Content**](./embedding.md) to create your own vectorstores and add them to your script of choice.
- Review one of the [**terminal examples**](./terminal_example.md) (`example/apps/*/terminal_*.py`) for a simple terminal interface.
