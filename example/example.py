from langgraph.graph.graph import CompiledGraph
from maeser.user_manager import UserManager, GithubAuthenticator
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.controllers import get_maeser_blueprint_with_user_management
from maeser.graphs.simple_rag import get_simple_rag
from flask import Blueprint, Flask
from flask_login import LoginManager

chat_logs_manager = ChatLogsManager("chat_logs")
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

homework_prompt: str = """You are an extremely helpful homework assistant. You should regularly refer back to the textbook and give exact section numbers to go back to.

    {context}
    """

labs_prompt: str = """You are an extremely helpful lab assistant. You should regularly refer back to the lab website and give links.
    The lab material also includes videos. If a video is available, embed the video using HTML. Use iframes for youtube videos and video elements for direct video links.
    If other media is available, like images, embed it similarly using img elements.

    You should also include a link to the lab website in your response if possible.

    {context}
    """

textbook_simple_rag: CompiledGraph = get_simple_rag("../verity/resources/vectorstore", "textbook", "chat_logs/hw.db", system_prompt_text=homework_prompt)
sessions_manager.register_branch("homework", "Homework", textbook_simple_rag)

labs_system_rag: CompiledGraph = get_simple_rag("../verity/resources/vectorstore", "labs", "chat_logs/labs.db", system_prompt_text=labs_prompt)
sessions_manager.register_branch("labs", "Labs", labs_system_rag)

github_authenticator = GithubAuthenticator("", "", "http://localhost:5000/login/github_callback")
user_manager = UserManager("chat_logs/users")
user_manager.register_authenticator("github", github_authenticator)
maeser_blueprint: Blueprint = get_maeser_blueprint_with_user_management(sessions_manager, user_manager)

app = Flask(__name__)
app.register_blueprint(maeser_blueprint)

app.secret_key = 'awkwerfnerfderf'  # Replace with a secure secret key
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "maeser.login" # type: ignore
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_full_id: str):
    auth_method, user_id = user_full_id.split('.', 1)
    return user_manager.get_user(auth_method, user_id)

if __name__ == "__main__":
    app.run()