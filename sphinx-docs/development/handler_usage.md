# Using Maeser with External Handlers

The **maeser.generate_response** module provides a unified interface for routing user input to Maeser’s chatbot sessions. It is designed to be handler-agnostic, allowing seamless integration with various interfaces such as Discord, Microsoft Teams, Flask-based UIs, and more.

Future plans for Maeser are to integrate handlers for several popular interfaces within the Maeser package itself. Currently, a Discord handler is provided in the **maeser.discord** package (see [**Setting Up a Discord Bot**](../user-setup/discord.md) for more information).

**maeser.generate_response** encapsulates the following:

- Session management via [**maeser.chat.chat_session_manager.ChatSessionManager**](../autodoc/maeser/maeser.chat.chat_session_manager.rst)
- Chat history tracking via [**maeser.chat.chat_logs.ChatLogsManager**](../autodoc/maeser/maeser.chat.chat_logs.rst)
- Bot configuration parsing ([**`bot.txt` format**](#bottxt-syntax))
- Dynamic graph creation using **LangGraph** and [**RAG Graphs**](./graphs.md)
- A single entrypoint function for all external handlers:  

  ```python
  handle_message(user_id: str, course_id: str, message_text: str) -> str
  ```

> **IMPORTANT:** **Please note that maeser.generate_response is new and has much room for refinement. If you run into issues using maeser.generate_response, please [report them on the Maeser GitHub](https://github.com/byu-cpe/Maeser/issues).**

---

## Core Functionality

### `handle_message(user_id, course_id, message_text)`

This function is to be called by the handler whenever a message is sent from any platform (Discord, Slack, Microsoft Teams, etc.). It returns a string which is the response of the bot.

- **Arguments**:
  - `user_id`: The unique string identifier for the user (e.g., Discord ID or session ID).
  - `course_id`: The string identifier corresponding to a configured course in the bot data directory.
    - This directory is defined in the `config.yaml` located in the working directory under the `vectorstore:vec_store_path` field. See `example_handlers/config_template.yaml` for an example config setup.
  - `message_text`: The user's question or input message.

- **Returns**:  
  A string representing the chatbot's final response message.

- **Behavior**:
  - Verifies and parses the bot configuration from `{bot_data_directory}/{course_id}/bot.txt`.
  - Registers a RAG Graph if not already registered for that course.
  - Tracks sessions across all interfaces with a global `session_key = user_id:course_id`.
  - Sends the message to the appropriate **LangGraph** session and returns the response.

---

## Required Files and Directory Structure

Ensure your course bot data is structured as follows:

```{code-block} text
:class: no-copybutton
bot_data
├── course1
│   ├── bot.txt
│   ├── dataset1
│   │   ├── index.faiss
│   │   └── index.pkl
│   ├── dataset2
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── ...
├── course2
│   └── ...
└── ...
```

While courses can be created manually, you should use the [**Admin Portal**](../user-setup/admin_portal.md) to build and modify course in `bot_data/` automatically.

<!-- Note from Adam:
- It may be a good idea in the future to supply a path to bot data path universally in the config file.
-->

## `bot.txt` Syntax

Each `bot.txt` must be structured like so:

```text
#NAME
course1
#RULES
rule1
rule2
rule3
#DATASETS
dataset1
dataset2
dataset3
```

- The names ("course1", "rule1", "dataset1") are placeholders, and there is no limit to the number of rules and datasets in a course.
- **WARNING:** Due to a file reading bug, there must be no empty lines in the bot.txt file for it to read.

While `bot.txt` can be altered manually, you should edit your courses using the [**Admin Portal**](../user-setup/admin_portal.md) to update `bot.txt` automatically.
