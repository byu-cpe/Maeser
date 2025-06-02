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
    LOG_SOURCE_PATH, OPENAI_API_KEY, VEC_STORE_PATH, CHAT_HISTORY_PATH, LLM_MODEL_NAME
)

import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

# A pipeline is a generalized prompt, often for providing answers across larger datasets,
# but still specific to relevant course information.
pipeline_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    Only answer questions about other things if the question asked does not relate directly to the context provided, but could be considered useful for the scope of the subject.
    If the question is unrelated to the subject entirely, redirect the user to the subject at hand.
    

    {context}
"""
from maeser.graphs.simple_rag import get_simple_rag
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
    memory_filepath=f"{VEC_STORE_PATH}/pipeline_memory.db",
    api_key=OPENAI_API_KEY, 
    system_prompt_text=(pipeline_prompt),
    model=LLM_MODEL_NAME)
  
sessions_manager.register_branch(branch_name="pipeline", branch_label="Pipeline", graph=byu_maeser_pipeline_rag)

from flask import Flask

base_app = Flask(__name__)

from maeser.blueprints import App_Manager

app_manager = App_Manager(
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
