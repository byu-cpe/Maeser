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

maeser_simple_rag: CompiledGraph = get_simple_rag("example/vectorstores/maeser", "index", "chat_logs/maeser.db", system_prompt_text=maeser_prompt)
sessions_manager.register_branch("maeser", "Karl G. Maeser History", maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag("example/vectorstores/byu", "index", "chat_logs/byu.db", system_prompt_text=byu_prompt)
sessions_manager.register_branch("byu", "BYU History", byu_simple_rag)

from maeser.user_manager import UserManager, GithubAuthenticator

github_authenticator = GithubAuthenticator("...", "...", "http://localhost:3000/login/github_callback")
user_manager = UserManager("chat_logs/users", max_requests=5, rate_limit_interval=60)
user_manager.register_authenticator("github", github_authenticator)

from flask import Flask

base_app = Flask(__name__)

from maeser.blueprints import add_flask_blueprint

app: Flask = add_flask_blueprint(
    base_app, 
    "secret",
    sessions_manager, 
    user_manager,
    app_name="Test App",
    chat_head="/static/Karl_G_Maeser.png",
    # Note that you can change other images too! We stick with the defaults for the logo and favicon.
    # main_logo_light="/static/main_logo_light.png",
    # favicon="/static/favicon.png",
)

if __name__ == "__main__":
    app.run(port=3000)
