# Terminal Example: Interactive CLI with Maeser

This guide illustrates how to use the official CLI example (`example/terminal_example.py`) to run Maeser in a terminal-based chat interface. You’ll inspect the script, configure settings, launch the example, and learn how to customize your own command‑line tutor.

---

## Prerequisites

- **Maeser development environment** set up (see `development_setup.md`).
- **Python 3.10+** virtual environment activated.
- **Maeser** installed in editable mode (`pip install -e .` or `make setup`).
- **Required FAISS vectorstores** built and available (via `embedding.md`).
- **`config.yaml`** configured with your OpenAI API key and file paths (see below).

---

## Configuring `config.yaml`

Copy the example and set these fields:

```yaml
# RAG memory storage path (SQLite files)
LOG_SOURCE_PATH: "path/to/chat_logs"
# OpenAI API key for LLM calls
OPENAI_API_KEY: "your-openai-key"
# Directory with FAISS vectorstores
VEC_STORE_PATH: "path/to/vectorstores"
# Path for chat history logs
CHAT_HISTORY_PATH: "path/to/chat_history"
# LLM model (e.g., gpt-4o)
LLM_MODEL_NAME: "gpt-4o"
```

These settings ensure the script can load your vectorstores, persist logs, and authenticate with OpenAI.

---

## Inspect `terminal_example.py`

Open **`example/terminal_example.py`** and explore its main sections:

### Imports & Environment Setup
```python
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from config_example import (
    LOG_SOURCE_PATH, OPENAI_API_KEY,
    VEC_STORE_PATH, CHAT_HISTORY_PATH,
    LLM_MODEL_NAME
)
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
```
- **ChatLogsManager** records all messages.  
- **ChatSessionManager** orchestrates branches and sessions.  
- **Config imports** supply file paths and keys.

### Prompt Definitions
```python
maeser_prompt: str = """
You are speaking from the perspective of Karl G. Maeser.
Answer questions about your life history only. {context}
"""

byu_prompt: str = """
You are speaking about the history of BYU.
Answer questions about BYU history only. {context}
"""
```
- Defines how the LLM should frame responses.

### Pipeline Registration
```python
from maeser.graphs.simple_rag import get_simple_rag
from maeser.graphs.pipeline_rag import get_pipeline_rag
from langgraph.graph.graph import CompiledGraph

# Simple RAG: Karl G. Maeser
a_graph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/maeser",
    memory_filepath=f"{LOG_SOURCE_PATH}/maeser.db",
    system_prompt_text=maeser_prompt,
    model=LLM_MODEL_NAME
)
sessions_manager.register_branch(
    branch_name="maeser",
    branch_label="Karl G. Maeser History",
    graph=a_graph
)

# Simple RAG: BYU History
b_graph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/byu",
    memory_filepath=f"{LOG_SOURCE_PATH}/byu.db",
    system_prompt_text=byu_prompt,
    model=LLM_MODEL_NAME
)
sessions_manager.register_branch(
    branch_name="byu",
    branch_label="BYU History",
    graph=b_graph
)

# Pipeline RAG: combine both domains
pipeline = get_pipeline_rag(
    vectorstore_config={
        "byu history": f"{VEC_STORE_PATH}/byu",
        "karl g maeser": f"{VEC_STORE_PATH}/maeser"
    },
    memory_filepath=f"{LOG_SOURCE_PATH}/pipeline_memory.db",
    api_key=OPENAI_API_KEY,
    system_prompt_text=(
        "You are a combined tutor for Maeser & BYU history. Use contexts: {context}"
    ),
    model=LLM_MODEL_NAME
)
sessions_manager.register_branch(
    branch_name="pipeline",
    branch_label="Pipeline",
    graph=pipeline
)
```
- **Registers three branches** for selection at runtime.

### CLI Menu & Session Loop
```python
import pyinputplus as pyip

print("Welcome to the Maeser terminal example!")
while True:
    # Build menu of branch labels
    choices = {v['label']: k for k, v in sessions_manager.branches.items()}
    choices["Exit terminal session"] = "exit"
    branch_label = pyip.inputMenu(
        list(choices.keys()), prompt="Select a branch:\n", numbered=True
    )
    if branch_label == "Exit terminal session":
        print("Exiting terminal session.")
        break
    branch = choices[branch_label]

    # Start a new conversation session
    sess = sessions_manager.get_new_session_id(branch)
    print(f"Session {sess} created for branch '{branch}'.")
    print("Type 'exit' or 'quit' to end the session.\n")

    # Converse until exit
    while True:
        user_input = input("User > ")
        if user_input.lower() in ("exit", "quit"):
            print("Session ended.\n")
            break
        response = sessions_manager.ask_question(user_input, branch, sess)
        print(f"System > {response['messages'][-1]}\n")
```
- **pyinputplus** creates a numbered menu for branch selection.  
- **get_new_session_id** initializes a fresh context.  
- **ask_question** sends user input to the chosen graph and returns the answer.

---

## Run the Terminal Example

Activate your venv and run:
```bash
python example/terminal_example.py
```
1. **Select** a branch (e.g., "Karl G. Maeser History").  
2. **Ask** questions and receive AI responses.  
3. Type **`exit`** or **`quit`** to end the session.

---

## Customization

- **Add Branches:** Register your own `CompiledGraph` before the loop.
- **Modify Prompts:** Tweak `maeser_prompt` and `byu_prompt` for tone and detail.
- **Change Menu Behavior:** Use `pyinputplus.inputMenu` parameters (e.g., `limit`, `timeout`).
- **Logging:** Adjust `ChatLogsManager` settings or paths for audit/analysis.

---

## Next Steps

- Explore the **Flask example** (`flask_example_user_mangement.py`) for web UI.
- Embed new knowledge bases via **`embedding.md`**.
- Design advanced workflows in **`custom_graphs.md`**.
- Review Maeser’s system architecture in **`architecture.md`**.

