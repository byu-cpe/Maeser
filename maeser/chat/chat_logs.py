# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Module for managing chat logs, including logging and retrieving chat history,
feedback, and training data.
"""

from maeser.user_manager import UserManager, User
from maeser.render import get_response_html
from abc import ABC, abstractmethod
from datetime import datetime
import time
import yaml
from os import path, stat, walk, mkdir, makedirs
import subprocess
from flask import abort, render_template
import platform


class BaseChatLogsManager(ABC):
    """Abstract base class for chat logs managers.

    Args:
        chat_log_path (str): Path to the chat log directory.
        user_manager (UserManager | None): Optional user manager instance.
    """

    def __init__(
        self, chat_log_path: str, user_manager: UserManager | None = None
    ) -> None:
        self.chat_log_path: str = chat_log_path
        self.user_manager: UserManager | None = user_manager

        # create log directory if it does not exist
        if not path.exists(self.chat_log_path):
            makedirs(self.chat_log_path)

    @abstractmethod
    def log(self, branch_name: str, session_id: str, log_data: dict) -> None:
        """
        Abstract method to log chat data.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged.

        Returns:
            None
        """
        pass

    @abstractmethod
    def log_feedback(
        self, branch_name: str, session_id: str, message_index: int, feedback: str
    ) -> None:
        """
        Abstract method to log feedback for a message.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            message_index (int): The index of the message to add feedback to.
            feedback (str): The feedback to add to the message.

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_chat_history_overview(self, user: User | None) -> list[dict]:
        """
        Abstract method to get an overview of chat history.
        This is used to display a list of overviews of previous chat conversations.

        Args:
            user (User | None): The user to get chat history for.

        Returns:
            list[dict]: A list of dictionaries containing information about previous chat conversations. Each should have the following keys:
                - 'branch': The name of the branch.
                - 'session': The session ID for the conversation.
                - 'modified': The timestamp of when the chat conversation was last modified.
                - 'header': The text that will be used as the link text. Usually the first message in the conversation. Could also be a conversation title.
        """
        pass

    @abstractmethod
    def get_chat_logs_overview(
        self,
        sort_by: str,
        order: str,
        branch_filter: str,
        user_filter: str,
        feedback_filter: str,
    ) -> tuple[list[dict], int, float, set[str]]:
        """
        Abstract method to get an overview of chat logs.

        Args:
            sort_by (str): The field to sort by.
            order (str): The order to sort by. Either 'asc' or 'desc'.
            branch_filter (str): The branch to filter by.
            feedback_filter (str): The feedback to filter by.

        Returns:
            tuple: A tuple containing:
                - list[dict]: A list of dictionaries containing information about chat logs.
                - int: The total number of tokens used.
                - float: The total cost of the chat logs.
        """
        pass

    @abstractmethod
    def get_chat_history(self, branch_name: str, session_id: str) -> dict:
        """
        Abstract method to get chat history for a session.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.

        Returns:
            dict: The chat history for the session.
        """
        pass

    @abstractmethod
    def get_log_file_template(self, filename: str, branch: str, app_name: str) -> str:
        """
        Abstract method to get the jinja template for a log file.

        Args:
            filename (str): The name of the log file.
            branch (str): The branch the log file is in.
            app_name (str): The display name of the Maeser application.

        Returns:
            str: The rendered template for the log file.
        """
        pass

    @abstractmethod
    def save_feedback(self, feedback: dict) -> None:
        """
        Abstract method to save feedback input to a file.

        Args:
            feedback (dict): The feedback to save.

        Returns:
            None
        """
        pass

    @abstractmethod
    def save_training_data(self, training_data: dict) -> None:
        """
        Abstract method to save training data to a file.

        Args:
            training_data (dict): The training data to save.

        Returns:
            None
        """
        pass


class ChatLogsManager(BaseChatLogsManager):
    """The Chat Logs Manager used by Maeser.

    Args:
        chat_log_path (str): Path to the chat log directory.
    """

    def __init__(self, chat_log_path: str) -> None:
        super().__init__(chat_log_path)

    def log(self, branch_name: str, session_id: str, log_data: dict) -> None:
        """
        Logs a user's message and chatbot's response with corresponding statistics to the session's chat log (in YAML format).

        This function should be called every time the user submits a new  message and receives
        a response from the chatbot.

        The **log_data** dictionary should contain the following key-value pairs:

        - "**messages**" (*tuple[str]*): A tuple of two strings: The user's message and the chatbot's response, in that order.
        - "**user**" (*User*): The user the chat belongs to.
        - "**cost**" (*float*): The total cost of the last message.
        - "**tokens**" (*int*): The total tokens of the last message.


        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged. Should contain the following keys: 'user', 'cost', 'tokens', and 'message'.

        Returns:
            None
        """
        if not self._does_log_exist(branch_name, session_id):
            self._create_log_file(branch_name, session_id, log_data.get("user", None))
        else:
            self._update_log_file(branch_name, session_id, log_data)

    def log_feedback(
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
        with open(
            f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "r"
        ) as file:
            log: dict = yaml.safe_load(file)
            log["messages"][message_index]["liked"] = feedback

        with open(
            f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "w"
        ) as file:
            yaml.dump(log, file)

    def get_chat_history_overview(self, user: User | None) -> list[dict]:
        """
        Gets an overview of chat history for a specific user.

        This overview consists of statistics for all chat logs that belongs to the user.

        The statistics for each chat log in the list include the following:

        - "**branch**" (*str*): The chat branch of the session.
        - "**session**" (*str*): The chat session ID.
        - "**modified**" (*int*): The time and date the log file was last modified.
        - "**header**" (*str*): The first message of the chat. This is used as the chat title in the web view.

        Args:
            user (User | None): The user to get chat history for.

        Returns:
            list[dict]: A list of dictionaries containing information about previous chat conversations.
        """
        overview = []
        conversations = self._get_file_list()
        for conversation in conversations:
            current_user_name: str = "anon" if user is None else user.full_id_name
            if current_user_name == conversation["user"]:
                overview.append(
                    {
                        "branch": conversation["branch"],
                        "session": conversation["name"].removesuffix(".log"),
                        "modified": conversation["modified"],
                        "header": conversation["first_message"],
                    }
                )
        # Sort conversations by date modified
        overview.sort(key=lambda x: x["modified"], reverse=True)

        # Remove conversations with no first message
        overview = [link for link in overview if link["header"] is not None]

        return overview

    def get_chat_logs_overview(
        self,
        sort_by: str,
        order: str,
        branch_filter: str,
        user_filter: str,
        feedback_filter: str,
    ) -> tuple[list[dict], int, float, set[str]]:
        """
        Gets an overview of chat logs.

        Retrieves information about individual chat logs that match the specified filters as well as
        the total tokens and cost aggregated from these logs.

        Details for individual chat logs include the following:

        - "**name**" (*str*): The name of the log file.
        - "**created**" (*int*): The creation time and date of the log file.
        - "**modified**" (*int*): The time and date the log file was last modified.
        - "**branch**" (*str*): The chat branch of the conversation.

        Args:
            sort_by (str): The field to sort by. Either 'created' or 'modified'.
            order (str):
                The order to sort by:

                - 'asc' for ascending order.
                - 'desc' for descending order.

            branch_filter (str): The branch to filter by.
            feedback_filter (str):
                The feedback to filter by:

                - 'true' for logs with feedback.
                - 'false' for logs without feedback.

        Returns:
            tuple: A tuple containing:
                - list[dict]: A list of dictionaries containing information about chat logs.
                - int: The total number of tokens used.
                - float: The total cost of the chat logs.
        """

        log_files = self._get_file_list()

        # Get set of all users
        user_set = {f["user"] for f in log_files}

        if branch_filter:
            log_files = [
                f for f in log_files if branch_filter.lower() in f["branch"].lower()
            ]

        if user_filter:
            log_files = [f for f in log_files if user_filter == f["user"]]

        if feedback_filter:
            feedback_filter_bool = feedback_filter.lower() == "true"
            log_files = [
                f for f in log_files if f["has_feedback"] == feedback_filter_bool
            ]

        reverse = order == "desc"
        log_files.sort(key=lambda x: x[sort_by], reverse=reverse)

        # Calculate aggregate number of tokens and cost
        total_tokens = 0
        total_cost = 0.0
        for file in log_files:
            with open(
                f"{self.chat_log_path}/chat_history/{file['branch']}/{file['name']}",
                "r",
            ) as f:
                log = yaml.safe_load(f)
                if log.get("total_tokens") is None:
                    print(
                        f'\x1b[33mWarning: "total_tokens" key is missing from log for file {file["name"]}, defaulting value to 0.\x1b[0m'
                    )
                else:
                    total_tokens += log.get("total_tokens", 0)
                if log.get("total_cost") is None:
                    print(
                        f'\x1b[33mWarning: "total_cost" key is missing from log for file {file["name"]}, defaulting value to 0.\x1b[0m'
                    )
                else:
                    total_cost += log.get("total_cost", 0.0)

        return log_files, total_tokens, total_cost, user_set

    def get_chat_history(self, branch_name: str, session_id: str) -> dict:
        """
        Retrieves chat history for a specific session.

        This loads the entire chat log file (in YAML format) as a dictionary,
        consisting of the following fields:

        - "**branch**": The chat branch of the session.
        - "**real_name**": The real name of the user.
        - "**session_id**": The chat session ID.
        - "**time**": The creation time of the session/chat log.
        - "**total_cost**": The aggregate cost of all messages in the chat.
        - "**total_tokens**": The aggregate number of tokens of all messages in the chat.
        - "**user**": The full ID of the user, formatted like ``authenticator.user_id``.
        - "**messages**":
            A list containing the chat message history, including the messages from both the user and the chatbot.

            - The "**content**" field contains the actual text content of the message.
            - The "**role**" field indicates whether the message came from the user ('user') or the chatbot ('system').
            - Messages from the chatbot ("role: system") also contain the context retrieved from vector stores ("**context**"), the total cost and tokens ("**cost**" and "**tokens_used**"), and the execution time ("**execution_time**").


        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.

        Returns:
            dict: The chat history for the session.
        """
        with open(
            f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "r"
        ) as file:
            chat_history = yaml.safe_load(file)
        return chat_history

    def get_log_file_template(self, filename: str, branch: str, app_name: str) -> str:
        """
        Gets the Jinja template for a log file.

        Args:
            filename (str): The name of the log file.
            branch (str): The branch the log file is in.
            app_name (str): The display name of the Maeser application.
                This name and the name of the branch will be populated into the page's title element.

        Returns:
            str: The rendered template for the log file.
        """

        def process_messages(messages: dict) -> dict:
            """
            Process each system response in the conversation and convert it to HTML.

            Args:
                filename (str): The name of the log file.

            Returns:
                dict: The processed messages in HTML format.
            """
            for message in messages:
                message["content"] = get_response_html(message["content"])

            return messages

        try:
            print(f"{self.chat_log_path}/chat_history/{branch}/{filename}")
            with open(
                f"{self.chat_log_path}/chat_history/{branch}/{filename}", "r"
            ) as file:
                content = yaml.safe_load(file)

            user_name = content["user"]
            real_name = content["real_name"]
            branch = content["branch"]
            time = content["time"]
            total_cost = round(content["total_cost"], 3)
            total_tokens = content["total_tokens"]

            try:
                messages = process_messages(content["messages"])
            except KeyError:
                messages = None

            return render_template(
                "display_chat_log.html",
                user_name=user_name,
                real_name=real_name,
                branch=branch,
                time=time,
                total_cost=total_cost,
                total_tokens=total_tokens,
                messages=messages,
                app_name=f"{branch} - {app_name}",
            )
        except FileNotFoundError:
            abort(404, description="Log file not found")
        except yaml.YAMLError as e:
            abort(500, description=f"Error parsing log file: {e}")

    def save_feedback(self, feedback: dict) -> None:
        """
        Saves feedback input to a YAML file.

        Args:
            feedback (dict): The feedback to save.

        Returns:
            None
        """

        # Make directory if it doesn't exist
        try:
            mkdir(f"{self.chat_log_path}/feedback")
        except FileExistsError:
            pass

        now = time.time()
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(now))
        filename = f"{self.chat_log_path}/feedback/{timestamp}.log"

        with open(filename, "w") as f:
            yaml.dump(feedback, f)

        print(f"Feedback saved to {filename}")

    def save_training_data(self, training_data: dict) -> None:
        """
        Saves training data to a YAML file.

        Args:
            training_data (dict): The training data to save.
        """

        # Make directory if it doesn't exist
        try:
            mkdir(f"{self.chat_log_path}/training_data")
        except FileExistsError:
            pass

        now = time.time()
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(now))
        filename = f"{self.chat_log_path}/training_data/{timestamp}.log"

        with open(filename, "w") as f:
            yaml.dump(training_data, f)

        print(f"Training data saved to {filename}")

    def _get_file_list(self) -> list[dict]:
        """
        Get the list of chat history files with metadata.

        The metadata for each log file includes the following:
        - "**name**" (*str*): The name of the log file.
        - "**created**" (*int*): The creation time and date of the log file.
        - "**modified**" (*int*): The time and date the log file was last modified.
        - "**branch**" (*str*): The chat branch of the conversation.

        Returns:
            list[dict]: List of all log files.
        """

        def get_creation_time(file_path):
            """Gets the time and date a file was created.

            Uses subprocess to run the shell command corresponding to the operating system
            for creation time retrieval.

            Currently only supports the ``stat`` command for macOS and Linux.

            Args:
                file_path (str): The path to the file.

            Raises:
                RuntimeError: _description_

            Returns:
                int: the creation time and date of the file.
            """
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ["stat", "-f", "%B", file_path], capture_output=True, text=True
                )
                if result.returncode != 0:
                    raise RuntimeError(f"Error getting creation time: {result.stderr}")
                return int(result.stdout.strip())
            elif platform.system() == "Linux":
                result = subprocess.run(
                    ["stat", "-c", "%W", file_path], capture_output=True, text=True
                )
                if result.returncode != 0:
                    raise RuntimeError(f"Error getting creation time: {result.stderr}")
                return int(result.stdout.strip())
            else:
                # Fallback for other operating systems
                return int(path.getctime(file_path))

        def get_file_info(file_path: str) -> dict:
            """
            Get detailed information from a file and return it as a dictionary.

            This information includes the following:
            - "**has_feedback**" (*bool*): Whether the user has submitted feedback in this chat.
            - "**first_message**" (*str*): The first message in the chat. This is used as the
            header/title of the chat in the web view.
            - "**user**" (*str*): The full ID of the user, formatted like ``authenticator.user_id``.
            - "**real_name**" (*str*): The real name of the user.

            Args:
                file_path (str): The path to the file.

            Returns:
                dict: A dictionary containing detailed information about the file.
            """

            def has_feedback(msgs: list) -> bool:
                for msg in msgs:
                    if "liked" in msg:
                        return True
                return False

            file_info = {}
            try:
                with open(file_path, "r") as file:
                    chat_log = yaml.safe_load(file)
                    file_info["has_feedback"] = has_feedback(
                        chat_log.get("messages", [])
                    )
                    file_info["first_message"] = (
                        chat_log.get("messages", [{}])[0]["content"]
                        if len(chat_log.get("messages", [])) > 0
                        else None
                    )
                    file_info["user"] = chat_log.get("user", "unknown user")
                    file_info["real_name"] = chat_log.get("real_name", "Student")
            except Exception as e:
                print(f"Error: Cannot read file {file_path}: {e}")
            return file_info

        file_list = []
        for root, dirs, files in walk(self.chat_log_path + "/chat_history"):
            for file_name in files:
                file_path = path.join(root, file_name)
                if path.isfile(file_path):  # Check if the path is a file
                    try:
                        created_time = get_creation_time(file_path)
                    except RuntimeError:
                        # Fallback if stat doesn't work at all (may show modified time)
                        created_time = int(path.getctime(file_path))

                    file_stat = stat(file_path)
                    file_info = {
                        "name": file_name,
                        "created": created_time,
                        "modified": file_stat.st_mtime,
                        "branch": path.basename(
                            root
                        ),  # Get the branch name from the directory
                    }
                    # Update file_info with additional details from get_file_info
                    file_info.update(get_file_info(file_path))
                    file_list.append(file_info)
        return file_list

    def _create_log_file(
        self, branch_name: str, session_id: str, user: User | None = None
    ) -> None:
        """
        Creates a new log file for a chat session.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            user (User | None): Optional User to obtain information from to include in the log.

        Returns:
            None
        """
        # compile log information
        log_info: dict = {
            "session_id": session_id,
            "user": user.full_id_name if user else "anon",
            "real_name": user.realname if user else "anon",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "branch": branch_name,
            "total_cost": 0,
            "total_tokens": 0,
            "messages": [],
        }

        # ensure log directory exists
        if not path.exists(f"{self.chat_log_path}/chat_history/{branch_name}"):
            makedirs(f"{self.chat_log_path}/chat_history/{branch_name}")

        # create log file
        with open(
            f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "w"
        ) as file:
            yaml.dump(log_info, file)

    def _update_log_file(
        self, branch_name: str, session_id: str, log_data: dict
    ) -> None:
        """
        Updates the log file with the new log data.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged. Should contain the following keys: "user_info", "cost", "tokens_used", and "message".

        Returns:
            None
        """
        with open(
            f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "r"
        ) as file:
            log: dict = yaml.safe_load(file)

            log["messages"] = log.get("messages", [])

            # Add user message
            log["messages"].append(
                {
                    "role": "user",
                    "content": log_data["messages"][-2],
                }
            )

            # Add chatbot message and execution stats
            log["messages"].append(
                {
                    "role": "system",
                    "content": log_data["messages"][-1],
                    "context": [
                        context.page_content
                        for context in log_data["retrieved_context"]
                    ],
                    "execution_time": log_data.get("execution_time", 0),
                    "tokens_used": log_data.get("tokens_used", 0),
                    "cost": log_data.get("cost", 0),
                }
            )

            log["total_cost"] += log_data.get("cost", 0)
            log["total_tokens"] += log_data.get("tokens_used", 0)

        with open(
            f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "w"
        ) as file:
            yaml.dump(log, file)

    def _does_log_exist(self, branch_name: str, session_id: str) -> bool:
        """
        Checks if a log file exists for the given session ID.

        Args:
            session_id (str): The session ID to check for.

        Returns:
            bool: True if the log file exists, False otherwise.
        """
        return path.exists(
            f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log"
        )
