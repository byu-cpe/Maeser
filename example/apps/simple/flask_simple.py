# SPDX-License-Identifier: LGPL-3.0-or-later

from example.apps.config import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, STATIC_FOLDER, VEC_STORE_PATH, CHAT_HISTORY_PATH, LLM_MODEL_NAME
)

import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

maeser_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history based on the context provided.
    If the question is unrelated to the topic or the context, politely inform the user that their questions is outside the context of your resources.

    {context}
    """

byu_prompt: str = """You are speaking about the history of Brigham Young University.
    You will answer a question about the history of BYU based on the context provided.
    If the question is unrelated to the topic or the context, politely inform the user that their questions is outside the context of your resources.

    {context}
    """

from maeser.graphs.simple_rag import get_simple_rag
from langgraph.graph.graph import CompiledGraph

maeser_simple_rag: CompiledGraph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/maeser",
    vectorstore_index="index",
    memory_filepath=f"{LOG_SOURCE_PATH}/maeser.db",
    api_key=OPENAI_API_KEY,
    system_prompt_text=maeser_prompt,
    model=LLM_MODEL_NAME,
)

sessions_manager.register_branch(branch_name="simple_maeser", branch_label="Karl G. Maeser History", graph=maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/byu",
    vectorstore_index="index",
    memory_filepath=f"{LOG_SOURCE_PATH}/byu.db",
    api_key=OPENAI_API_KEY,
    system_prompt_text=byu_prompt,
    model=LLM_MODEL_NAME,
)

sessions_manager.register_branch(branch_name="simple_byu", branch_label="BYU History", graph=byu_simple_rag)

from flask import Flask

# Default resources must be relative to the directory the Flask script is located in (regardless of current working directory)
app_dir = os.path.dirname(__file__)

# Configure base app
base_app = Flask(
    __name__,
    static_folder=os.path.relpath(STATIC_FOLDER, app_dir),
)

from maeser.blueprints import AppManager

app_manager = AppManager(
    app=base_app,
    app_name="Maeser Test App -- NO USER MANAGER",
    flask_secret_key="secret",
    chat_session_manager=sessions_manager,
    chat_head="/static/Karl_G_Maeser.png"
    # Note that you can change other aspects too! Heres some examples below
    # main_logo_login="/static/main_logo_login.png",
    # favicon="/static/favicon.png",
    # login_text="Welcome to Maeser. This package is designed to facilitate the creation of Retrieval-Augmented Generation (RAG) chatbot applications, specifically tailored for educational purposes."
    # primary_color="#f5f5f5"
)

# Initalize the flask blueprint
app: Flask = app_manager.add_flask_blueprint()

if __name__ == "__main__":
    app.run(port=3002)
