# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Module for managing chat sessions and interactions with multiple chat interfaces.
"""

from maeser.chat.chat_logs import BaseChatLogsManager
from maeser.user_manager import User
import time
from uuid import uuid4 as uid
from langchain_community.callbacks import get_openai_callback
from langgraph.graph.graph import CompiledGraph


class ChatSessionManager:
    """
    Manages and directs sessions for multiple chat interfaces.

    Args:
        chat_logs_manager (BaseChatLogsManager | None):
            The chat logs manager to use for logging chat data.
            This can be a ChatLogsManager object or a custom chat logs manager
            that inherits from BaseChatLogsManager.

    Returns:
        None
    """

    def __init__(
        self,
        chat_logs_manager: BaseChatLogsManager | None = None,
    ) -> None:
        self.chat_logs_manager: BaseChatLogsManager | None = chat_logs_manager
        self.graphs: dict = {}

    def register_branch(
        self, branch_name: str, branch_label: str, graph: CompiledGraph
    ) -> None:
        """
        Registers a new chat branch with its name, label, and compiled RAG graph.

        See maeser.graphs for built-in RAG graphs.

        Args:
            branch_name (str): The name of the branch.
            branch_label (str): The label of the branch.
            graph (CompiledGraph): The compiled RAG graph for the branch.

        Returns:
            None
        """
        self.graphs[branch_name] = {"label": branch_label, "graph": graph}

    def get_new_session_id(self, branch_name: str, user: User | None = None) -> str:
        """
        Creates a new chat session for the given branch and user.
        Includes creating a new log file for the session.

        If no user is provided, "anon" will be used in place of ``authenticator.user_id``.

        Args:
            branch_name (str): The action of the branch to create a session for.
            user (User | None): The user to create the session for.

        Returns:
            str: The session ID for the new session.
        """
        # Generate session ID with user information if it exists
        if user:
            session_id: str = f"{uid()}-{user.auth_method}-{user.ident}"
        else:
            session_id: str = f"{uid()}-anon"

        # Create log file if chat logs manager is available
        if self.chat_logs_manager:
            self.chat_logs_manager.log(branch_name, session_id, {"user": user})

        return session_id

    def ask_question(self, message: str, branch_name: str, sess_id: str) -> dict:
        """
        Asks a question in a specific session of a branch.

        Args:
            message (str): The question to ask.
            branch_name (str): The chat branch to ask the question in.
            sess_id (str): The session ID to ask the question in.

        Returns:
            dict: The response to the question.
        """
        config = {"configurable": {"thread_id": sess_id}}
        start_time = time.time()
        # Get token count for the response
        with get_openai_callback() as cb:
            response = self.graphs[branch_name]["graph"].invoke(
                {
                    "messages": [message],
                },
                config=config,
            )
            response["tokens_used"] = cb.total_tokens
            response["cost"] = cb.total_cost
        end_time = time.time()
        execution_time = end_time - start_time

        response["execution_time"] = execution_time

        if self.chat_logs_manager:
            self.chat_logs_manager.log(branch_name, sess_id, response)

        return response

    def add_feedback(
        self, branch_name: str, session_id: str, message_index: int, feedback: str
    ) -> None:
        """
        Adds feedback to the log for a specific response in a specific session.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            message_index (int): The index of the message to add feedback to.
            feedback (str): The feedback to add to the message.

        Returns:
            None
        """
        # Return if no chat logs manager
        if not self.chat_logs_manager:
            return

        self.chat_logs_manager.log_feedback(
            branch_name, session_id, message_index, feedback
        )

    def get_conversation_history(self, branch_name: str, session_id: str) -> dict:
        """
        Gets the conversation history for a specific session in a specific branch.

        Args:
            branch_name (str): The action of the branch to get the conversation history from.
            session_id (str): The session ID to get the conversation history from.

        Returns:
            dict: The conversation history for the session.
        """
        if not self.chat_logs_manager:
            return {}

        return self.chat_logs_manager.get_chat_history(branch_name, session_id)

    @property
    def branches(self) -> dict:
        """dict: The list of branches available for chat."""
        return self.graphs

    @property
    def chat_log_path(self) -> str | None:
        """str | None: The path to the logs directory."""
        return self.chat_logs_manager.chat_log_path if self.chat_logs_manager else None
