# Maeser Project: Building an AI-Powered Homework and Lab Assistant

This README will guide you through the process of setting up and understanding the Maeser project, an AI-powered assistant for homework and lab work. We'll break down the main `example.py` into manageable parts, explaining each section as we go.

Be sure to follow the [development setup](./development_setup.md) instructions before this to install required packages. 

## Step 1: Import Required Modules

First, let's import all the necessary modules:

```python
from langgraph.graph.graph import CompiledGraph
from maeser.user_manager import UserManager, GithubAuthenticator
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.controllers import get_maeser_blueprint_with_user_management
from maeser.graphs.simple_rag import get_simple_rag
from flask import Blueprint, Flask
from flask_login import LoginManager
```

These imports include custom modules from the Maeser project, as well as Flask and LangGraph components.

## Step 2: Set Up Chat Logs and Session Management

Next, we'll set up the chat logs and session management:

```python
chat_logs_manager = ChatLogsManager("chat_logs")
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)
```

This creates a `ChatLogsManager` to handle chat logs and a `ChatSessionManager` to manage chat sessions.

## Step 3: Define System Prompts

Now, let's define the system prompts for homework and lab assistants:

```python
homework_prompt: str = """You are an extremely helpful homework assistant. You should regularly refer back to the textbook and give exact section numbers to go back to.

    {context}
    """

labs_prompt: str = """You are an extremely helpful lab assistant. You should regularly refer back to the lab website and give links.
    The lab material also includes videos. If a video is available, embed the video using HTML. Use iframes for youtube videos and video elements for direct video links.
    If other media is available, like images, embed it similarly using img elements.

    You should also include a link to the lab website in your response if possible.

    {context}
    """
```

These prompts define the behavior and capabilities of our AI assistants.

## Step 4: Set Up RAG (Retrieval-Augmented Generation) Systems

Next, we'll set up the RAG systems for both homework and labs:

```python
textbook_simple_rag: CompiledGraph = get_simple_rag("../verity/resources/vectorstore", "textbook", "chat_logs/hw.db", system_prompt_text=homework_prompt)
sessions_manager.register_branch("homework", "Homework", textbook_simple_rag)

labs_system_rag: CompiledGraph = get_simple_rag("../verity/resources/vectorstore", "labs", "chat_logs/labs.db", system_prompt_text=labs_prompt)
sessions_manager.register_branch("labs", "Labs", labs_system_rag)
```

This creates two RAG systems, one for homework and one for labs, and registers them with the session manager. These functions to retrieve these Simple RAG systems return example langgraph graphs. You can replace these with any custom graph you would like to use.

## Step 5: Set Up User Authentication

Now, let's set up user authentication using GitHub:

```python
github_authenticator = GithubAuthenticator("", "", "http://localhost:5000/login/github_callback")
user_manager = UserManager("chat_logs/users")
user_manager.register_authenticator("github", github_authenticator)
```

This sets up GitHub authentication and a user manager. Note: You'll need to fill in your GitHub OAuth credentials in the `GithubAuthenticator` constructor.

## Step 6: Create Flask Application and Blueprint

Next, we'll create the Flask application and register the Maeser blueprint:

```python
maeser_blueprint: Blueprint = get_maeser_blueprint_with_user_management(sessions_manager, user_manager)

app = Flask(__name__)
app.register_blueprint(maeser_blueprint)
```

This creates a Flask application and registers the Maeser blueprint with it.

## Step 7: Configure Flask-Login

Now, let's set up Flask-Login for managing user sessions:

```python
app.secret_key = 'awkwerfnerfderf'  # Replace with a secure secret key
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "maeser.login" # type: ignore
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_full_id: str):
    auth_method, user_id = user_full_id.split('.', 1)
    return user_manager.get_user(auth_method, user_id)
```

This configures Flask-Login and sets up a user loader function.

## Step 8: Run the Application

Finally, we'll add the code to run the Flask application:

```python
if __name__ == "__main__":
    app.run()
```

This allows you to run the script directly to start the Flask development server.

## Running the Application

To run the application:

1. Make sure you have all the required dependencies installed.
2. Set up your GitHub OAuth credentials and replace the empty strings in the `GithubAuthenticator` constructor.
3. Replace the `app.secret_key` with a secure secret key.
4. Run the script using Python:

```
python example/example.py
```

The server should start, and you can access the application at `http://localhost:5000`.