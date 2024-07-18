from langgraph.graph.graph import CompiledGraph
from maeser.user_manager import UserManager, GithubAuthenticator
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.controllers import get_maeser_blueprint_without_user_management, get_maeser_blueprint_with_user_management
from maeser.controllers import chat_interface
from maeser.graphs.simple_rag import get_simple_rag
from flask import Blueprint, Flask, session, url_for
from flask_login import LoginManager, login_required

chat_logs_manager = ChatLogsManager("chat_logs")
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

textbook_simple_rag: CompiledGraph = get_simple_rag("...", "textbook", "...")
sessions_manager.register_branch("homework", "Homework", textbook_simple_rag)

labs_system_rag: CompiledGraph = get_simple_rag("...", "labs", "...")
sessions_manager.register_branch("labs", "Labs", labs_system_rag)

github_authenticator = GithubAuthenticator("...", "...", "...")
user_manager = UserManager("chat_logs/users")
user_manager.register_authenticator("github", github_authenticator)
maeser_blueprint: Blueprint = get_maeser_blueprint_with_user_management(sessions_manager, user_manager)

app = Flask(__name__)
app.register_blueprint(maeser_blueprint)

app.secret_key = 'awkwerfnerfderf'  # Replace with a secure secret key
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "maeser.login"
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_full_id: str):
    auth_method, user_id = user_full_id.split('.', 1)
    return user_manager.get_user(auth_method, user_id)

if __name__ == "__main__":
    app.run()