# Maeser Example (with Terminal Interface)

This README explains an example program that demonstrates how to use the `maeser` package to create a simple conversational AI application with multiple chat branches in a terminal interface.

The `example/terminal_example.py` file's code is shown below. You can run the example application by running:

```shell
python example/terminal_example.py
```

but first some overview and setup is needed so read on.

## Overview

The example program sets up a terminal-based application with two different chat branches: one for Karl G. Maeser's history and another for BYU's history. It uses a simple command-line interface for user interaction.

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
from langgraph.graph.graph import CompiledGraph

maeser_simple_rag: CompiledGraph = get_simple_rag("example/vectorstores/maeser", "index", "chat_logs/maeser.db", system_prompt_text=maeser_prompt)
sessions_manager.register_branch("maeser", "Karl G. Maeser History", maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag("example/vectorstores/byu", "index", "chat_logs/byu.db", system_prompt_text=byu_prompt)
sessions_manager.register_branch("byu", "BYU History", byu_simple_rag)
```

This section sets up two RAG graphs, one for each chat branch, and registers them with the session manager. RAG enhances the AI's responses by retrieving relevant information from a knowledge base.

> **NOTE:** The `get_simple_rag` function could be replaced with any LangGraph compiled state graph. So, for a custom application, you will likely want to create a custom graph and register it with the sessions manager. For more instructions on creating custom graphs, see [Using Custom Graphs](./graphs.md)

### Terminal Interface Setup

```python
import pyinputplus as pyip

print("Welcome to the Maeser terminal example!")

while True:
    # structure branches dictionary for input menu
    label_to_key = {value['label']: key for key, value in sessions_manager.branches.items()}
    label_to_key["Exit terminal session"] = "exit"

    # select a branch
    branch = pyip.inputMenu(
        list(label_to_key.keys()),
        prompt="Select a branch: \n",
        numbered=True
    )

    # get the key for the selected branch
    if branch != "Exit terminal session":
        branch = label_to_key[branch]
    else:
        print("Exiting terminal session.")
        break

    # create a new session
    session = sessions_manager.get_new_session_id(branch)
    print(f"\nSession {session} created for branch {branch}.")
    print("Type 'exit' to end the session.\n")

    # loop for conversation
    while True:
        # get user input
        user_input = input("User:\n> ")

        # check for exit
        if user_input == "exit" or user_input == 'quit':
            print("Session ended.\n")
            break

        # get response
        response = sessions_manager.ask_question(user_input, branch, session)

        print(f"\nSystem:\n{response['messages'][-1]}\n")
```

This section sets up the terminal interface using the `pyinputplus` library. It creates a menu for selecting chat branches, manages sessions, and handles user input and system responses.

You could implement whatever logic in this interface you would like, including loading previous chat sessions. In this example, we kept it simple. 

## Running the Application

To run the application, you can now run:

```shell
python example/terminal_example.py
```

This will start the terminal interface. You'll be presented with a menu to choose between the Karl G. Maeser history branch, the BYU history branch, or to exit the application. Once you select a branch, you can start asking questions. Type 'exit' or 'quit' to end a session and return to the branch selection menu.

## Customization

You can customize various aspects of the application, such as:

- Adding more chat branches
- Modifying the prompts for existing branches
- Changing the user interface (e.g., adding color, improving formatting)
- Implementing error handling and input validation

Here, we discuss a few of these.

### Adding a New Chat Branch

To add a new chat branch:

1. Define a new prompt for the branch:

   ```python
   new_prompt: str = """You are an expert on [topic].
       You will answer questions about [topic] based on the context provided.
       Don't answer questions about other things.

       {context}
       """
   ```

2. Create and register a new RAG graph:

   ```python
   new_simple_rag: CompiledGraph = get_simple_rag("path/to/vectorstore", "index", "chat_logs/new_topic.db", system_prompt_text=new_prompt)
   sessions_manager.register_branch("new_topic", "New Topic Name", new_simple_rag)
   ```

### Modifying the User Interface

You can enhance the user interface by using libraries like `colorama` for colored output or by adding more formatting to the responses. For example:

```python
from colorama import Fore, Style

# In the conversation loop:
print(f"\n{Fore.GREEN}System:{Style.RESET_ALL}\n{response['messages'][-1]}\n")
```

## Conclusion

This example demonstrates how to use the `maeser` package to create a multi-branch chatbot application with a terminal interface. You can build upon this example to create more complex applications tailored to your specific needs, whether for command-line tools or as a starting point for more advanced interfaces.