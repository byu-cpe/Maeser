# Terminal Example: Interactive CLI with Maeser

This guide illustrates how to use the terminal example scripts to run Maeser in a command-line interface.

The `example/apps/` directory contains three terminal examples:

- `simple/terminal_simple.py`
- `pipeline/terminal_pipeline.py`
- `universal/terminal_universal.py`

For more information on the simple, pipeline, and universal examples, see [**Maeser Example (with Flask & User Management)**](./flask_example.md). This guide will demonstrate the terminal interface using `universal/terminal_universal.py`. However, you may follow along with any of the example terminal scripts.

---

## Prerequisites

- **Maeser development environment** (see [**Development Setup**](development_setup)).
- **Pre-built FAISS Vector Stores** at the paths referenced in your `config.yaml` file. The example scripts use the pre-built `byu` and `maeser` vector stores found in `example/resources/vectorstores`. See [**Embedding New Content**](embedding) for instructions on how to build and add your own vector stores.

---

## Configuring `config.yaml`

Maeser uses a simple config file for API keys and directories. To set up configuration, **make a copy of `example/apps/config_template.yaml`** and name it **`config.yaml`**.

Configure the following fields in your `config.yaml` file:

```{code-block} yaml
:class: no-copybutton
### An OpenAI API key is required for LLM calls ###

api_keys:
  openai_api_key: '<openai_api_key_here>'

# ---Other configuration options found here--- #

### Configure the LLM and text embedding models ###

llm:
  llm_model_name: gpt-4o-mini
  llm_provider: openai
  token_limit: 400
```

**Field Descriptions**:

- **openai_api_key**: Key to authenticate with OpenAI’s API.
- **llm_** entries: Configuration for your LLM.

> **Note:** Feel free to change other fields in `config.yaml` according to your needs (such as `vec_store_path` or `max_requests`). Since the terminal examples do not have user management, you can skip the GitHub and LDAP fields.

---

## Inspect The Terminal Example Scripts

The following sections will go through `universal/terminal_universal.py` section-by-section and explain how the code works. If you are only interested in running the script, then skip to [**Run the Terminal Example**](#run-the-terminal-example).

Most of the code can be left unchanged and should work as-is assuming that your `config.yaml` file is configured correctly. If your are using a different example script, pay attention to the notes at the bottom of each section explaining any differences.

### Imports & Environment Setup

Imports necessary Maeser modules and config variables and sets the OpenAI API key in the environment.

```python
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from example.apps.config import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, VEC_STORE_PATH, CHAT_HISTORY_PATH, LLM_MODEL_NAME
)
import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
```

### Chat Logs & Session Manager Setup

Initializes **chat log management** and **session management** to track conversations and user queries.

```python
chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)
```

### Prompt Definitions

Defines system prompts that give the chatbot its rules and personality.

```python
# The prompt for a Universal RAG is a generalized prompt, often for providing answers across larger datasets,
# but still specific to relevant course information.
universal_prompt: str = """You are speaking from the perspective of Karl G. Maeser.
    You will answer a question about your own life history or the history of BYU based on 
    the context provided.
    If the question is unrelated to the topic or the context, politely inform the user that their question is outside the context of your resources.
    
    {context}
"""
```

The `{context}` text is required and will be replaced with actual context from the vector stores when the chatbot is generating a response.

> **Note:** The `simple/terminal_simple.py` script has one prompt for each vector store, whereas the scripts in `universal/` and `pipeline/` share one prompt across all vector stores.

### RAG Graph Construction

Creates a **Retrieval Augmented Generation (RAG) graph** for the chatbot to follow and registers the graph with the sessions manager.

```python
# One for the history of BYU and one for the life of Karl G. Maeser.
# Ensure that topics are all lower case and spaces between words
vectorstore_config = {
    "byu history": f"{VEC_STORE_PATH}/byu",      # Vector Store for BYU history.
    "karl g maeser": f"{VEC_STORE_PATH}/maeser"  # Vector Store for Karl G. Maeser.
}

byu_maeser_universal_rag: CompiledGraph = get_universal_rag(
    vectorstore_config=vectorstore_config,
    memory_filepath=f"{LOG_SOURCE_PATH}/universal_memory.db",
    api_key=OPENAI_API_KEY,
    system_prompt_text=(universal_prompt),
    model=LLM_MODEL_NAME,
)

sessions_manager.register_branch(branch_name="universal", branch_label="BYU and Karl G. Maeser History", graph=byu_maeser_universal_rag)
```

> **Note:** The `simple/terminal_simple.py` script creates and registers one RAG graph for each individual vector store, whereas the scripts in `universal/` and `pipeline/` create one branch that accesses all vector stores.

### CLI Menu & Session Loop

This is your way of interfacing with the model, in the absence of a more standard GUI.

```python
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

- **pyinputplus** creates a numbered menu for branch selection.  
- **get_new_session_id** initializes a fresh context.  
- **ask_question** sends user input to the chosen graph and returns the answer.

---

## Run the Terminal Example

[**Activate your venv**](./development_setup.md#activating-the-virtual-environment) and run:

```bash
python example/terminal_example.py
```

1. **Select a branch** (e.g., "Karl G. Maeser History").
2. **Ask questions** and receive AI responses.
3. Type **`exit`** or **`quit`** to end the session.

---

## Next Steps

- Explore the [**Flask examples**](./flask_example.md) for web UI.
- Embed new knowledge bases for use with Maeser (see [**Embedding New Content**](./embedding.md)).
- Learn more about the Simple, Pipeline, and Universal RAG in [**Graphs**](./graphs.md).
- Review Maeser’s system architecture in [**Architecture Overview**](./architecture.md).
