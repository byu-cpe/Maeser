# SPDX-License-Identifier: LGPL-3.0-or-later

from example.apps.config import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, STATIC_FOLDER, VEC_STORE_PATH, CHAT_HISTORY_PATH, LLM_MODEL_NAME,
)

import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

# The prompt for a Pipeline RAG is a generalized prompt, often for providing answers across larger datasets,
# but still specific to relevant course information.
pipeline_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    If the question is unrelated to the topic or the context, politely inform the user that their question is outside the context of your resources.
    
    {context}
"""

from maeser.graphs.pipeline_rag import get_pipeline_rag
from langgraph.graph.graph import CompiledGraph

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
    system_prompt_text=(pipeline_prompt),
    model=LLM_MODEL_NAME,
)
  
sessions_manager.register_branch(branch_name="pipeline", branch_label="BYU and Karl G. Maeser History", graph=byu_maeser_pipeline_rag)

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

# Initialize the flask blueprint
app: Flask = app_manager.add_flask_blueprint()

if __name__ == "__main__":
    app.run(port=3002)
