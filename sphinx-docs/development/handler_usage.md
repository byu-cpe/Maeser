# Using `generate_response.py` with External Handlers

The `generate_response.py` module provides a unified interface for routing user input to Maeser’s RAG-powered chatbot sessions. It is designed to be handler-agnostic, allowing seamless integration with various interfaces such as Discord, Microsoft Teams, Flask-based UIs, and more.

---

**`generate_response.py`**  
  Located at the root of the project, this script encapsulates:
  - Session management via `ChatSessionManager`
  - Chat history tracking via `ChatLogsManager`
  - Bot configuration parsing (`bot.txt` format)
  - Dynamic graph creation using `LangGraph` and RAG pipelines
  - A single entrypoint function for all external handlers:  
    ```python
    handle_message(user_id: str, course_id: str, message_text: str) -> str
    ```

---

## Core Functionality

### `handle_message(user_id, course_id, message_text)`

This function is to be called by the handler whenever a message is sent from any platform (discord, teams, etc.). It returns a string which is the response of the bot. 

- **Arguments**:
  - `user_id`: Unique string identifier for the user (e.g., Discord ID or session ID)
    - This thould be used for user tracking. As it stands, the current `webapp_handler.md` does not have any authentication that could be used to pass in an ID.
  - `course_id`: String identifier corresponding to a configured course in `v2/bot_data`
    - This path is defined in the config.yaml under the `vec_store_path`.
  - `message_text`: The user's question or input message

- **Returns**:  
  A string representing Maeser's final response message

- **Behavior**:
  - Verifies and parses the bot configuration from `v2/bot_data/{course_id}/bot.txt`
  - Registers a RAG pipeline if not already registered for that course
  - Tracks sessions across all interfaces with a global `session_key = user_id:course_id`
  - Sends the message to the appropriate `LangGraph` session and returns the response

---

## Required Files and Directory Structure

Ensure your course bot data is structured as follows:
```
v2/
├── bot_data/
│ ├── course1/
│ │ ├── bot.txt
│ │ ├── dataset_1/
│ │ │ ├── index.faiss
│ │ │ └── index.pkl
│ └── course2/
...
```
- If the flask webapp is used to generate courses, this should all be done automatically. 

- It may be a good idea in the future to supply a path to bot data path universally in the config file.

Each `bot.txt` must contain:

```
#NAME
#RULES
Always answer with citations.
#DATASETS
course_notes
```
Due to a file reading bug, there must be no empty lines in the bot.txt file for it to read.

**Please note that a lot of this is currently held up with popsicle sticks and glue, and is not refined by any means. There is still a lot of work to be done, especially with importing data like filepaths instead of using literals.**