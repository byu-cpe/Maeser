# SPDX-License-Identifier: LGPL-3.0-or-later

import os

# Import Maeser components
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.graphs.universal_rag import get_universal_rag
from langgraph.graph.graph import CompiledGraph

# Import configuration
from maeser.config import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, VEC_STORE_PATH, CHAT_HISTORY_PATH, LLM_MODEL_NAME
)

# Set API key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Path to the bot data directory
BOT_DATA_PATH = VEC_STORE_PATH

# Managers
chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

# Unified session tracking for Maeser: {session_key (user_id:course_id): maeser_session_id}
# This dictionary will hold the Maeser chat session IDs for ALL interfaces (Discord, Teams, etc.)
global_maeser_sessions = {}

# --- Utility Functions (shared by all bot handlers) ---

def parse_data_from_bot_txt(path):
    """Parses a bot config file to extract rules and datasets."""
    sections = {}
    current_header = None
    buffer = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                if current_header:
                    sections[current_header] = buffer if len(buffer) > 1 else buffer[0] if buffer else ""
                current_header = line[1:].lower()
                buffer = []
            elif current_header:
                buffer.append(line)

        # Save the last section
        if current_header:
            sections[current_header] = buffer if len(buffer) > 1 else buffer[0] if buffer else ""

    return sections

def get_valid_course_ids():
    """Retrieves a list of valid course IDs from the bot_data directory."""

    if not os.path.exists(BOT_DATA_PATH):
        print("Error: bot_data directory not found. Please ensure it exists with course subdirectories.")
        return []
    return [
        name for name in os.listdir(BOT_DATA_PATH)
        if os.path.isdir(os.path.join(BOT_DATA_PATH, name))
    ]

def register_branch(branch_name:str, course_id:str, bot_config_path:str):
    """Registers a branch to the session handler.

    Args:
        branch_name (str): The name to give the branch.
        course_id (str): The ID for the course to be registered. This should match the name of the course's vector store directory
        bot_config_path (str): The path to `bot.txt` for the course's chatbot.
    """
    parsed_data = parse_data_from_bot_txt(bot_config_path)
    
    # Ensure required keys exist in parsed data
    if "rules" not in parsed_data or "datasets" not in parsed_data:
        return f"Error: 'rules' or 'datasets' section missing in bot.txt for course '{course_id}'."

    rules = parsed_data["rules"]
    datasets = parsed_data["datasets"]
    if isinstance(datasets, str):
        datasets = [datasets]

    vectorstore_config = {
        dataset: os.path.join(VEC_STORE_PATH, course_id, dataset) for dataset in datasets
    }
    ruleset = "\n".join(rules) + "\n{context}\n"

    universal_rag: CompiledGraph = get_universal_rag(
        vectorstore_config=vectorstore_config,
        memory_filepath=f"{LOG_SOURCE_PATH}/universal_memory_{course_id}.db",
        api_key=OPENAI_API_KEY,
        system_prompt_text=ruleset,
        model=LLM_MODEL_NAME
    )

    sessions_manager.register_branch(
        branch_name=branch_name,
        branch_label=f"Universal-{course_id}",
        graph=universal_rag
    )
    print(f"Registered Maeser bot branch for course: {course_id}")


# --- Main Chat Handling Function (Unified Logic) ---

def handle_message(user_id: str, course_id: str, message_text: str) -> str:
    """Handles a message from any interface, routing it to the correct Maeser session.
    Manages bot registration and session creation for Maeser.

    Args:
        user_id (str): The unique string identifier for the user.
        course_id (str): The string identifier corresponding to a configured course in `vec_store_path` (defined in `config.yaml`).
        message_text (str): The user's question or input message.

    Returns:
        str: A string representing the chatbot's final response message.
    """
    # Verify bot config exists for the given course ID
    bot_config_path = f"{BOT_DATA_PATH}/{course_id}/bot.txt"
    if not os.path.exists(bot_config_path):
        return f"Bot config for course '{course_id}' not found. Please ensure the course ID is valid and configured."
    
    branch_name = f"universal_{course_id}"

    # Register the Maeser bot branch if it hasn't been registered yet
    if branch_name not in sessions_manager.branches:
        register_branch(branch_name, course_id, bot_config_path)

    # Get or create a Maeser session for the unique user+course combination
    session_key = f"{user_id}:{course_id}"
    if session_key not in global_maeser_sessions:
        maeser_session_id = sessions_manager.get_new_session_id(branch_name)
        global_maeser_sessions[session_key] = maeser_session_id
        print(f"Started new Maeser session '{maeser_session_id}' for user '{user_id}' in course '{course_id}'.")
    else:
        maeser_session_id = global_maeser_sessions[session_key]

    # Ask the question to the Maeser session and return the reply
    response = sessions_manager.ask_question(message_text, branch_name, maeser_session_id)
    return response['messages'][-1]
