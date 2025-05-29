"""
© 2024 Blaine Freestone, Brent Nelson, Gohaun Manley

This file is part of the Maeser usage example.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import threading
import asyncio # Needed for running Discord bot client
import subprocess # For ngrok
import time # For ngrok delay and main thread loop

# Import Maeser components
from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.graphs.pipeline_rag import get_pipeline_rag
from langgraph.graph.graph import CompiledGraph

# Import configuration
from config import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, VEC_STORE_PATH, CHAT_HISTORY_PATH, LLM_MODEL_NAME, DISCORD_BOT_TOKEN
)

# Set API key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Managers
chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

# Unified session tracking for Maeser: {session_key (user_id:course_id): maeser_session_id}
# This dictionary will hold the Maeser chat session IDs for ALL interfaces (Discord, Teams, etc.)
global_maeser_sessions = {}

# --- Utility Functions (shared by all bot handlers) ---

def parse_vectorstores_from_bot_txt(path):
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
    bot_data_path = "v2/bot_data"
    if not os.path.exists(bot_data_path):
        print("Error: bot_data directory not found. Please ensure it exists with course subdirectories.")
        return []
    return [
        name for name in os.listdir(bot_data_path)
        if os.path.isdir(os.path.join(bot_data_path, name))
    ]

# --- Main Chat Handling Function (Unified Logic) ---

def handle_message(user_id: str, course_id: str, message_text: str) -> str:
    """
    Handles a message from any interface, routing it to the correct Maeser session.
    Manages bot registration and session creation for Maeser.
    """
    # Verify bot config exists for the given course ID
    bot_config_path = f"v2/bot_data/{course_id}/bot1.txt"
    if not os.path.exists(bot_config_path):
        return f"Bot config for course '{course_id}' not found. Please ensure the course ID is valid and configured."
    
    branch_name = f"pipeline_{course_id}"

    # Register the Maeser bot branch if it hasn't been registered yet
    if branch_name not in sessions_manager.branches:
        parsed_data = parse_vectorstores_from_bot_txt(bot_config_path)
        
        # Ensure required keys exist in parsed data
        if "rules" not in parsed_data or "datasets" not in parsed_data:
            return f"Error: 'rules' or 'datasets' section missing in bot1.txt for course '{course_id}'."

        rules = parsed_data["rules"]
        datasets = parsed_data["datasets"]

        vectorstore_config = {
            dataset: f"{VEC_STORE_PATH}/{dataset}" for dataset in datasets
        }

        ruleset = "\n".join(rules) + "\n{context}\n"

        pipeline_rag: CompiledGraph = get_pipeline_rag(
            vectorstore_config=vectorstore_config,
            memory_filepath=f"{LOG_SOURCE_PATH}/pipeline_memory_{course_id}.db",
            api_key=OPENAI_API_KEY,
            system_prompt_text=ruleset,
            model=LLM_MODEL_NAME
        )

        sessions_manager.register_branch(
            branch_name=branch_name,
            branch_label=f"Pipeline-{course_id}",
            graph=pipeline_rag
        )
        print(f"Registered Maeser bot branch for course: {course_id}")

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


# --- Utility for Ngrok (for local testing of webhook-based bots like Teams) ---

TEAMS_BOT_LOCAL_PORT = 3978 # Standard default port for Bot Framework bots

def start_ngrok_tunnel(port: int):
    """
    Starts an ngrok tunnel to expose the local server to the internet.
    This is necessary for webhook-based bots (like Teams) to receive messages locally.
    """
    print(f"Attempting to start ngrok tunnel for port {port}...")
    try:
        # Check if ngrok is already running (e.g., from a previous run)
        # This is a basic check and might not catch all scenarios
        # You can also manually check with `ngrok http ${port}` and look for already bound errors.
        # This Popen command starts ngrok in the background.
        # "--log=stdout" outputs logs to stdout/stderr, which are then redirected to DEVNULL.
        # A more robust solution would be to parse ngrok's API for the URL.
        subprocess.Popen(["ngrok", "http", str(port), "--log=stdout"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5) # Give ngrok a few seconds to establish the tunnel
        print(f"Ngrok tunnel for port {port} started. Check your ngrok console for the public URL.")
        print(f"Remember to update your Teams bot messaging endpoint in Azure with this ngrok URL + '/api/messages'.")
    except FileNotFoundError:
        print("Error: 'ngrok' command not found.")
        print("Please ensure ngrok is installed and added to your system's PATH.")
        print("Download ngrok from: https://ngrok.com/download")
    except Exception as e:
        print(f"An unexpected error occurred while starting ngrok: {e}")

# --- Main Application Entry Point ---

if __name__ == "__main__":
    print("Starting Maeser Multi-Interface Application...")

    # Import bot handlers. They rely on the functions defined above in terminal_script.
    import discord_handler
    import teams_bot_runner

    # --- Launch Discord Bot ---
    # Discord bot needs to run its asyncio event loop in a separate thread
    print("Launching Discord Bot in a background thread...")
    discord_thread = threading.Thread(
        target=lambda: asyncio.run(discord_handler.client.start(DISCORD_BOT_TOKEN)),
        daemon=True # Daemon thread will exit when main program exits
    )
    discord_thread.start()
    print("Discord bot initiated.")

    # --- Launch Teams Bot (FastAPI Server) ---
    # The FastAPI server also needs to run in a separate thread as uvicorn.run() is blocking.
    print(f"Launching Teams Bot FastAPI server on port {TEAMS_BOT_LOCAL_PORT} in a background thread...")
    teams_server_thread = threading.Thread(
        target=lambda: teams_bot_runner.start_teams_bot_server(TEAMS_BOT_LOCAL_PORT),
        daemon=True
    )
    teams_server_thread.start()
    print("Teams bot server initiated.")

    # --- Start Ngrok Tunnel for Local Teams Testing ---
    # This is crucial for local development of webhook-based bots.
    start_ngrok_tunnel(TEAMS_BOT_LOCAL_PORT)

    print("\nMaeser application is now running. Interact via Discord or Microsoft Teams.")
    print("Press Ctrl+C to stop the application.")

    # Keep the main thread alive so that the daemon threads (bots) continue to run.
    try:
        while True:
            time.sleep(1) # Sleep to prevent busy-waiting
    except KeyboardInterrupt:
        print("\nApplication stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"An unexpected error occurred in the main application loop: {e}")