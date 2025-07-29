# SPDX-License-Identifier: LGPL-3.0-or-later

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

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

# The prompt for a Universal RAG is a generalized prompt, often for providing answers across larger datasets,
# but still specific to relevant course information.
universal_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    If the question is unrelated to the topic or the context, politely inform the user that their questions is outside the context of your resources.
    
    {context}
"""

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
  
sessions_manager.register_branch(branch_name="universal", branch_label="BYU and Karl G. Maeser History", graph=byu_maeser_universal_rag)

from maeser.user_manager import UserManager, GithubAuthenticator, LDAPAuthenticator

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

user_manager = UserManager(db_file_path=USERS_DB_PATH, max_requests=MAX_REQUESTS, rate_limit_interval=RATE_LIMIT_INTERVAL)
user_manager.register_authenticator(name="github", authenticator=github_authenticator)
user_manager.register_authenticator(name=LDAP3_NAME, authenticator=ldap3_authenticator) # If you are not using LDAP, comment out this line

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
    # Note that you can change other aspects too! Heres some examples below
    # main_logo_login="/static/main_logo_login.png",
    # favicon="/static/favicon.png",
    # login_text="Welcome to Maeser. This package is designed to facilitate the creation of Retrieval-Augmented Generation (RAG) chatbot applications, specifically tailored for educational purposes."
    # primary_color="#f5f5f5"
    # Please also check the documentation for further customization options!
)

# Initalize the flask blueprint
app: Flask = app_manager.add_flask_blueprint()

if __name__ == "__main__":
    app.run(port=3002)
