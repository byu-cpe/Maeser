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

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from config_example import (
    LOG_SOURCE_PATH, OPENAI_API_KEY, VEC_STORE_PATH, CHAT_HISTORY_PATH, LLM_MODEL_NAME
)
import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

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

from maeser.graphs.simple_rag import get_simple_rag
from maeser.graphs.pipeline_rag import get_pipeline_rag
from langgraph.graph.graph import CompiledGraph

maeser_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path=f"{VEC_STORE_PATH}/maeser", vectorstore_index="index", memory_filepath=f"{LOG_SOURCE_PATH}/maeser.db", system_prompt_text=maeser_prompt, model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="maeser", branch_label="Karl G. Maeser History", graph=maeser_simple_rag)

byu_simple_rag: CompiledGraph = get_simple_rag(vectorstore_path=f"{VEC_STORE_PATH}/byu", vectorstore_index="index", memory_filepath=f"{LOG_SOURCE_PATH}/byu.db", system_prompt_text=byu_prompt, model=LLM_MODEL_NAME)
sessions_manager.register_branch(branch_name="byu", branch_label="BYU History", graph=byu_simple_rag)

# One for the history of BYU and one for the life of Karl G. Maeser.
# Ensure that topics are all lower case and spaces between words
# These are specific prompts engineered for certain contexts.
vectorstore_config = {
    "byu history": f"{VEC_STORE_PATH}/byu",      # Vectorstore for BYU history.
    "karl g maeser": f"{VEC_STORE_PATH}/maeser"  # Vectorstore for Karl G. Maeser.
}

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
