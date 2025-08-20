# Using Maeser with External Handlers

The `dynamic_implementations/generate_response.py` module provides a unified interface for routing user input to Maeser’s RAG-powered chatbot sessions. It is designed to be handler-agnostic, allowing seamless integration with various interfaces such as Discord, Microsoft Teams, Flask-based UIs, and more. A few implementations of this workflow can be found [**in the `dynamic_implementations/` directory**](#dynamic-implementations-of-generate_responsepy).

This script encapsulates the following:

- Session management via `ChatSessionManager`
- Chat history tracking via `ChatLogsManager`
- Bot configuration parsing (`bot.txt` format)
- Dynamic graph creation using `LangGraph` and RAG pipelines
- A single entrypoint function for all external handlers:  

  ```python
  handle_message(user_id: str, course_id: str, message_text: str) -> str
  ```

> **IMPORTANT:** **Please note that a lot of this is currently held up with popsicle sticks and glue, and is not refined by any means. There is still a lot of work to be done, especially with importing data like filepaths instead of using literals.** In a future release, `generate_response.py` will be integrated directly into the Maeser package; for now, it is an external Python script that uses Maeser's internal RAG graph and session/logs managers.

---

## Core Functionality

### `handle_message(user_id, course_id, message_text)`

This function is to be called by the handler whenever a message is sent from any platform (Discord, Slack, Microsoft Teams, etc.). It returns a string which is the response of the bot.

- **Arguments**:
  - `user_id`: The unique string identifier for the user (e.g., Discord ID or session ID).
  - `course_id`: The string identifier corresponding to a configured course in `dynamic_implementations/bot_data`.
    - This path is defined in `dynamic_implementations/config.yaml` under the `vec_store_path` field.
  - `message_text`: The user's question or input message.

- **Returns**:  
  A string representing the chatbot's final response message.

- **Behavior**:
  - Verifies and parses the bot configuration from `dynamic_implementations/bot_data/{course_id}/bot.txt`.
  - Registers a RAG pipeline if not already registered for that course.
  - Tracks sessions across all interfaces with a global `session_key = user_id:course_id`.
  - Sends the message to the appropriate `LangGraph` session and returns the response.

---

## Required Files and Directory Structure

Ensure your course bot data is structured as follows:

```{code-block} text
:class: no-copybutton
dynamic_implementations/
└── bot_data
    ├── course1
    │   ├── bot.txt
    │   ├── dataset1
    │   ├── dataset2
    │   └── ...
    ├── course2
    │   └── ...
    └── ...
...
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

## Dynamic Implementations of `generate_response.py`

A few simple implementations of `generate_response.py` can be found in the `dynamic_implementations/` directory:

- **`discord_handler.py`:** Integrates Maeser with the Discord API to create custom Discord chatbots. For instructions on setting up your own discord bot, see [**Setting Up a Discord Bot**](../user-setup/discord.md).
- **`webapp_handler.py`:** An implementation of Maeser using only `generate_response.py`. This is simply a proof-of-concept for how a more generalized Maeser API could interact with a web interface.
