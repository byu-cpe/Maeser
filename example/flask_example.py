"""
© 2024 Blaine Freestone, Carson Bush, Brent Nelson

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

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager("chat_logs")
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

from maeser.graphs.simple_rag import get_simple_rag
from langgraph.graph.graph import CompiledGraph

maeser_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path="vectorstores/maeser", vectorstore_index="index", memory_filepath="chat_logs/maeser.db", system_prompt_text=maeser_prompt)
sessions_manager.register_branch(branch_name="maeser", branch_label="Karl G. Maeser History", graph=maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path="vectorstores/byu", vectorstore_index="index", memory_filepath="chat_logs/byu.db", system_prompt_text=byu_prompt)
sessions_manager.register_branch(branch_name="byu", branch_label="BYU History", graph=byu_simple_rag)

from flask import Flask

base_app = Flask(__name__)

from maeser.blueprints import add_flask_blueprint

app: Flask = add_flask_blueprint(
    app=base_app, 
    flask_secret_key="secret",
    chat_session_manager=sessions_manager, 
    app_name="Test App",
    chat_head="/static/Karl_G_Maeser.png",
    # Note that you can change other images too! We stick with the defaults for the logo and favicon.
    # main_logo_light="/static/main_logo_light.png",
    # favicon="/static/favicon.png",
)

if __name__ == "__main__":
    app.run(port=3000)
