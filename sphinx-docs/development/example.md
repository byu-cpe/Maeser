# Maeser Package Example

This README explains an example program that demonstrates how to use the `maeser` package to create a simple conversational AI application with multiple chat branches and user authentication.

The `example/example.py` file's code is shown below. You can run the example application by running:
```shell
python example/example.py
```

## Overview

The example program sets up a Flask web application with two different chat branches: one for Karl G. Maeser's history and another for BYU's history. It uses GitHub authentication for user management and implements rate limiting.

## Key Components

### 1. Chat Management

```python
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager("chat_logs")
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)
```

These lines initialize the chat logs and session managers, which handle storing and managing chat conversations.

### 2. Prompt Definition

```python
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
```

Here, we define system prompts for two different chat branches. These prompts set the context and behavior for the AI in each branch.

### 3. RAG (Retrieval-Augmented Generation) Setup

```python
from maeser.graphs.simple_rag import get_simple_rag

maeser_simple_rag: CompiledGraph = get_simple_rag("example/vectorstores/maeser", "index", "chat_logs/maeser.db", system_prompt_text=maeser_prompt)
sessions_manager.register_branch("maeser", "Karl G. Maeser History", maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag("example/vectorstores/byu", "index", "chat_logs/byu.db", system_prompt_text=byu_prompt)
sessions_manager.register_branch("byu", "BYU History", byu_simple_rag)
```

This section sets up two RAG graphs, one for each chat branch, and registers them with the session manager. RAG enhances the AI's responses by retrieving relevant information from a knowledge base.

> **NOTE:** The `get_simple_rag` function could be replaced with any LangGraph compiled state graph. So, for a custom application, you will likely want to create a custom graph and register it with the sessions manager. For more instructions on creating custom graphs, see [Using Custom Graphs](./graphs.md)

### 4. User Management and Authentication

```python
from maeser.user_manager import UserManager, GithubAuthenticator

github_authenticator = GithubAuthenticator("...", "...", "http://localhost:5000/login/github_callback")
user_manager = UserManager("chat_logs/users", max_requests=5, rate_limit_interval=60)
user_manager.register_authenticator("github", github_authenticator)
```

Here, we set up user management with GitHub authentication and implement rate limiting (5 requests updated every 60 seconds).

### 5. Flask Application Setup

```python
from flask import Flask
from maeser.blueprints import add_flask_blueprint

base_app = Flask(__name__)

app: Flask = add_flask_blueprint(
    base_app, 
    "secret",
    sessions_manager, 
    user_manager,
    app_name="Test App",
    chat_head="/static/Karl_G_Maeser.png",
)
```

Finally, we create a Flask application and add the Maeser blueprint to it, configuring various options like the app name and chat head image.

> **NOTE:** For a custom application, you may choose to not use the `add_flask_blueprint` function but rather create your own Flask app.
The Flask app should call the proper methods in the chat sessions manager. 

## Running the Application

To run the application, simply execute the script:

```python
if __name__ == "__main__":
    app.run()
```

This starts the Flask development server.

## Customization

You can customize various aspects of the application, such as:

- Adding more chat branches
- Changing the authentication method(s)
- Modifying the rate limiting parameters
- Updating the app name, chat head, logo, or favicon

## Conclusion

This example demonstrates how to use the `maeser` package to create a multi-branch chatbot application with user authentication and rate limiting. You can build upon this example to create more complex applications tailored to your specific needs.