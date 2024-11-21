# Maeser Example (with Flask)

This README explains an example program that demonstrates how to use the `maeser` package to create a simple conversational AI application with multiple chat branches and user authentication that is rendered on a Flask web server. The example program is located in the `example` directory of Maeser.

The program is contained in `flask_example.py` and its code is shown below. You can run the example application by running:

```shell
python flask_example.py
```

but first some overview and setup is needed so read on.

## Overview

The example program sets up a Flask web application with two different chat branches: one for Karl G. Maeser's history and another for BYU's history.

## Key Components

### Chat Management

```python
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager

chat_logs_manager = ChatLogsManager("chat_logs")
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)
```

These lines initialize the chat logs and session managers, which handle storing and managing chat conversations.

### Prompt Definition

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

### RAG (Retrieval-Augmented Generation) Setup

```python
from maeser.graphs.simple_rag import get_simple_rag

maeser_simple_rag: CompiledGraph = get_simple_rag("vectorstores/maeser", "index", "chat_logs/maeser.db", system_prompt_text=maeser_prompt)
sessions_manager.register_branch("maeser", "Karl G. Maeser History", maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag("vectorstores/byu", "index", "chat_logs/byu.db", system_prompt_text=byu_prompt)
sessions_manager.register_branch("byu", "BYU History", byu_simple_rag)
```

This section sets up two RAG graphs, one for each chat branch, and registers them with the session manager. RAG enhances the AI's responses by retrieving relevant information from a knowledge base.

> **NOTE:** The `get_simple_rag` function could be replaced with any LangGraph compiled state graph. So, for a custom application, you will likely want to create a custom graph and register it with the sessions manager. For more instructions on creating custom graphs, see [Using Custom Graphs](./graphs.md)

### Flask Application Setup

```python
from flask import Flask
from maeser.blueprints import add_flask_blueprint

base_app = Flask(__name__)

app: Flask = add_flask_blueprint(
    base_app,
    "secret",
    sessions_manager,
    app_name="Test App",
    chat_head="static/Karl_G_Maeser.png",
)
```

Finally, we create a Flask application and add the Maeser blueprint to it, configuring various options like the app name and chat head image.

> **NOTE:** For a custom application, you may choose to not use the `add_flask_blueprint` function but rather create your own Flask app.
> The Flask app should call the proper methods in the chat sessions manager.

## Running the Application

To run the application, you can now run:

```shell
python flask_example.py
```

This should start up a local server. Opening a web browser to the address it tells you to use will bring up the example app.

## User Management and Authentication

A common thing to add to an app like this is user authentication, giving your app some control over who is using the app. Here, we will show how to modify `flask_example.py` to use authentication. We will register a `GithubAuthenticator` with a `UserManager`. This means that our application will use Github OAuth to authenticate users in the application. This will require you to register a GithHub OAuth Application.

### Code Changes to `flask_example.md`

First, you need to add the following lines of code to `flask_example.md`:

```python
from maeser.user_manager import UserManager, GithubAuthenticator

github_authenticator = GithubAuthenticator("...", "...", "http://localhost:3000/login/github_callback")
user_manager = UserManager("chat_logs/users", max_requests=5, rate_limit_interval=60)
user_manager.register_authenticator("github", github_authenticator)

```

Add these before the line that starts with:

```python
from flask import Flask
```

The second change to make is to add one parameter to the `add_flask_blueprint()` call in the code. The new call is like this:

```python
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
```

As you can see, a `user_manager` parameter has been added to the call.

### Registering Your GitHub OAuth App

Before you can run the app you need to register it with GitHub at the GitHub website.

1. Go to GitHub Developer Settings:

   - Navigate to your GitHub account settings.
   - Click on "Developer settings" in the sidebar.
   - Choose "OAuth Apps."
   - Click the "New OAuth App" button.

2. Fill in App Details:

   - Application name: Choose a descriptive name (e.g., "Maeser Example").
   - Homepage URL: Enter http://127.0.0.1:3000
   - Authorization callback URL: Enter http://localhost:3000/login/github_callback

3. Register and Get Credentials:

   - Click "Register application."
   - You'll be taken to your new app's page.
   - Note down the following:
     - Client ID: A long string of characters.
     - Client Secret: Click "Generate a new client secret" and save the value.

> **NOTE:** Keep your client secret confidential. Never share it publicly.

4. Using the Credentials in the maeser example:

   Replace `...` placeholders in the `GithubAuthenticator` instantiation first with the client ID and then with the client secret. This will be in the lines of code you were instructed to add above.

   ```python
   from maeser.user_manager import UserManager, GithubAuthenticator

   github_authenticator = GithubAuthenticator("<your client ID>", "<your client secret>", "http://localhost:3000/login/github_callback")
   user_manager = UserManager("chat_logs/users", max_requests=5, rate_limit_interval=60)
   user_manager.register_authenticator("github", github_authenticator)
   ```

Here, we set up user management with GitHub authentication and implement rate limiting (5 requests updated every 60 seconds).

## Customization

Moving on, you could customize various aspects of the application, such as:

- Changing the port the server runs on
- Adding more chat branches
- Modifying the rate limiting parameters
- Updating the app name, chat head, logo, or favicon

## Conclusion

This example demonstrates how to use the `maeser` package to create a multi-branch chatbot Web application with user authentication and rate limiting. You can build upon this example to create more complex applications tailored to your specific needs.
