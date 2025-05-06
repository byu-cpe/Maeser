"""
© 2024 Blaine Freestone, Carson Bush, Brent Nelson, Gohaun Manley

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

from config_example import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, USERS_DB_PATH, 
    VEC_STORE_PATH, MAX_REQUESTS, RATE_LIMIT_INTERVAL, 
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_AUTH_CALLBACK_URI, 
    GITHUB_TIMEOUT, CHAT_HISTORY_PATH, LDAP3_NAME, 
    LDAP_SERVER_URLS, LDAP_BASE_DN, LDAP_ATTRIBUTE_NAME, LDAP_SEARCH_FILTER, 
    LDAP_OBJECT_CLASS, LDAP_ATTRIBUTES, LDAP_CA_CERT_PATH, LDAP_CONNECTION_TIMEOUT, 
    LLM_MODEL_NAME
)

import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

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

pipeline_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    Don't answer questions about other things.

    {context}
"""

from maeser.graphs.simple_rag import get_simple_rag
from maeser.graphs.pipeline_rag import get_pipeline_rag
from langgraph.graph.graph import CompiledGraph

maeser_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path=f"{VEC_STORE_PATH}/maeser", vectorstore_index="index", memory_filepath=f"{LOG_SOURCE_PATH}/maeser.db", system_prompt_text=maeser_prompt, model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="maeser", branch_label="Karl G. Maeser History", graph=maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path=f"{VEC_STORE_PATH}/byu", vectorstore_index="index", memory_filepath=f"{LOG_SOURCE_PATH}/byu.db", system_prompt_text=byu_prompt, model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="byu", branch_label="BYU History", graph=byu_simple_rag)

# One for the history of BYU and one for the life of Karl G. Maeser.
# Ensure that topics are all lower case and spaces between words
vectorstore_config = {
    "byu history": f"{VEC_STORE_PATH}/byu",      # Vectorstore for BYU history.
    "karl g maeser": f"{VEC_STORE_PATH}/maeser"  # Vectorstore for Karl G. Maeser.
}

byu_maeser_pipeline_rag: CompiledGraph = get_pipeline_rag(
    vectorstore_config=vectorstore_config, 
    memory_filepath=f"{LOG_SOURCE_PATH}/pipeline_memory.db",
    api_key=OPENAI_API_KEY, 
    system_prompt_text=pipeline_prompt,
    model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="pipeline", branch_label="Pipeline", graph=byu_maeser_pipeline_rag)

from maeser.user_manager import UserManager, GithubAuthenticator, LDAPAuthenticator

# Replace the '...' with a client id and secret from a GitHub OAuth App that you generate in the config_example.yaml
github_authenticator = GithubAuthenticator(
    client_id=GITHUB_CLIENT_ID, 
    client_secret=GITHUB_CLIENT_SECRET, 
    auth_callback_uri=GITHUB_AUTH_CALLBACK_URI,
    timeout=GITHUB_TIMEOUT,
    max_requests=MAX_REQUESTS
)
# Replace the '...' in the config_example.yaml with all the proper configurations
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
user_manager.register_authenticator(name=LDAP3_NAME, authenticator=ldap3_authenticator)

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
    # Note that you can change other aspects too! Heres some examples below
    # main_logo_login="/static/main_logo_login.png",
    # favicon="/static/favicon.png",
    # login_text="Welcome to Maeser. This package is designed to facilitate the creation of Retrieval-Augmented Generation (RAG) chatbot applications, specifically tailored for educational purposes."
    # primary_color="#f5f5f5"
    # Please also check the documentation for further customization options!
)

#initalize the flask blueprint
app: Flask = app_manager.add_flask_blueprint()

if __name__ == "__main__":
    app.run(port=3002)
