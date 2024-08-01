"""
Module for managing chat logs, including logging and retrieving chat history,
feedback, and training data.

© 2024 Blaine Freestone, Carson Bush

This file is part of Maeser.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
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
    def __init__(self, chat_log_path: str, user_manager: UserManager | None = None) -> None:
        """
        Initializes the BaseChatLogsManager.

        Args:
            chat_log_path (str): Path to the chat log directory.
            user_manager (UserManager | None): Optional user manager instance.
        """
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
    def log_feedback(self, branch_name: str, session_id: str, message_index: int, feedback: str) -> None:
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
    def get_chat_logs_overview(self, sort_by: str, order: str, branch_filter: str, feedback_filter: str) -> tuple[list[dict], int, float]:
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
    def get_log_file_template(self, filename: str, branch: str) -> str:
        """
        Abstract method to get the jinja template for a log file.

        Args:
            filename (str): The name of the log file.
            branch (str): The branch the log file is in.

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
    def __init__(self, chat_log_path: str) -> None:
        """
        Initializes the ChatLogsManager.

        Args:
            chat_log_path (str): Path to the chat log directory.
        """
        super().__init__(chat_log_path)

    def log(self, branch_name: str, session_id: str, log_data: dict) -> None:
        """
        Logs chat data to a YAML file.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged. Should contain the following keys: 'user', 'cost', 'tokens', and 'message'.

        Returns:
            None
        """
        if not self._does_log_exist(branch_name, session_id):
            self._create_log_file(branch_name, session_id, log_data.get('user', None))
        else:
            self._update_log_file(branch_name, session_id, log_data)

    def log_feedback(self, branch_name: str, session_id: str, message_index: int, feedback: str) -> None:
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
        with open(f'{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log', 'r') as file:
            log: dict = yaml.safe_load(file)
            log['messages'][message_index]['liked'] = feedback

        with open(f'{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log', 'w') as file:
            yaml.dump(log, file)

    def get_chat_history_overview(self, user: User | None) -> list[dict]:
        """
        Gets an overview of chat history.

        Args:
            user (User | None): The user to get chat history for.

        Returns:
            list[dict]: A list of dictionaries containing information about previous chat conversations.
        """
        overview = []
        conversations = self._get_file_list()
        for conversation in conversations:
            current_user_name: str = 'anon' if user is None else user.full_id_name
            if current_user_name == conversation['user']:
                overview.append({
                    'branch': conversation['branch'],
                    'session': conversation['name'].removesuffix('.log'),
                    'modified': conversation['modified'],
                    'header': conversation['first_message']
                })
        # Sort conversations by date modified
        overview.sort(key=lambda x: x['modified'], reverse=True)

        # Remove conversations with no first message
        overview = [link for link in overview if link['header'] is not None]

        return overview

    def get_chat_logs_overview(self, sort_by: str, order: str, branch_filter: str, feedback_filter: str) -> tuple[list[dict], int, float]:
        """
        Gets an overview of chat logs.

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
        log_files = self._get_file_list()

        if branch_filter:
            log_files = [f for f in log_files if branch_filter.lower() in f['branch'].lower()]

        if feedback_filter:
            feedback_filter_bool = feedback_filter.lower() == 'true'
            log_files = [f for f in log_files if f['has_feedback'] == feedback_filter_bool]

        reverse = (order == 'desc')
        log_files.sort(key=lambda x: x[sort_by], reverse=reverse)

        # Calculate aggregate number of tokens and cost
        total_tokens = 0
        total_cost = 0.0
        for file in log_files:
            with open(f'{self.chat_log_path}/chat_history/{file["branch"]}/{file["name"]}', 'r') as f:
                log = yaml.safe_load(f)
                total_tokens += log.get('tokens', 0)
                total_cost += log.get('cost', 0.0)

        return log_files, total_tokens, total_cost

    def get_chat_history(self, branch_name: str, session_id: str) -> dict:
        """
        Retrieves chat history for a specific session.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.

        Returns:
            dict: The chat history for the session.
        """
        with open(f'{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log', 'r') as file:
            chat_history = yaml.safe_load(file)
        return chat_history

    def get_log_file_template(self, filename: str, branch: str) -> str:
        """
        Gets the Jinja template for a log file.

        Args:
            filename (str): The name of the log file.
            branch (str): The branch the log file is in.

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
                message['content'] = get_response_html(message['content'])
            
            return messages

        try:
            print(f'{self.chat_log_path}/chat_history/{branch}/{filename}')
            with open(f'{self.chat_log_path}/chat_history/{branch}/{filename}', 'r') as file:
                content = yaml.safe_load(file)
            
            user_name = content['user']
            real_name = content['real_name']
            branch = content['branch']
            time = content['time']
            total_cost = round(content['total_cost'], 3)
            total_tokens = content['total_tokens']
            
            try:
                messages = process_messages(content['messages'])
            except KeyError:
                messages = None
            
            return render_template(
                'display_chat_log.html',
                user_name=user_name,
                real_name=real_name,
                branch=branch,
                time=time,
                total_cost=total_cost,
                total_tokens=total_tokens,
                messages=messages,
                app_name=branch
            )
        except FileNotFoundError:
            abort(404, description='Log file not found')
        except yaml.YAMLError as e:
            abort(500, description=f'Error parsing log file: {e}')

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
            mkdir(f'{self.chat_log_path}/feedback')
        except FileExistsError:
            pass

        now = time.time()
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(now))
        filename = f'{self.chat_log_path}/feedback/{timestamp}.log'

        with open(filename, 'w') as f:
            yaml.dump(feedback, f)

        print(f'Feedback saved to {filename}')

    def save_training_data(self, training_data: dict) -> None:
        """
        Saves training data to a YAML file.

        Args:
            training_data (dict): The training data to save.
        """

        # Make directory if it doesn't exist
        try:
            mkdir(f'{self.chat_log_path}/training_data')
        except FileExistsError:
            pass

        now = time.time()
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(now))
        filename = f'{self.chat_log_path}/training_data/{timestamp}.log'

        with open(filename, 'w') as f:
            yaml.dump(training_data, f)

        print(f'Training data saved to {filename}')

    def _get_file_list(self) -> list[dict]:
        """
        Get the list of chat history files with metadata.

        Returns:
            bool: True if the log file exists, False otherwise.
        """
        def get_creation_time(file_path):
            if platform.system() == 'Darwin':  # macOS
                result = subprocess.run(['stat', '-f', '%B', file_path], capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"Error getting creation time: {result.stderr}")
                return int(result.stdout.strip())
            elif platform.system() == 'Linux':
                result = subprocess.run(['stat', '-c', '%W', file_path], capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"Error getting creation time: {result.stderr}")
                return int(result.stdout.strip())
            else:
                # Fallback for other operating systems
                return int(path.getctime(file_path))
        
        def get_file_info(file_path: str) -> dict:
            """
            Get detailed information from a file and return it as a dictionary.

            Args:
                file_path (str): The path to the file.

            Returns:
                dict: A dictionary containing detailed information about the file.
            """
            def has_feedback(msgs: list) -> bool:
                for msg in msgs:
                    if 'liked' in msg:
                        return True
                return False
            
            file_info = {}
            try:
                with open(file_path, 'r') as file:
                    chat_log = yaml.safe_load(file)
                    file_info['has_feedback'] = has_feedback(chat_log.get('messages', []))
                    file_info['first_message'] = chat_log.get('messages', [{}])[0]["content"] if len(chat_log.get('messages', [])) > 0 else None
                    file_info['user'] = chat_log.get('user', 'unknown user')
                    file_info['real_name'] = chat_log.get('real_name', 'Student')
            except Exception as e:
                print(f"Error: Cannot read file {file_path}: {e}")
            return file_info

        file_list = []
        for root, dirs, files in walk(self.chat_log_path + '/chat_history'):
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
                        'name': file_name,
                        'created': created_time,
                        'modified': file_stat.st_mtime,
                        'branch': path.basename(root),  # Get the branch name from the directory
                    }
                    # Update file_info with additional details from get_file_info
                    file_info.update(get_file_info(file_path))
                    file_list.append(file_info)
        return file_list

    def _create_log_file(self, branch_name: str, session_id: str, user: User | None = None) -> None:
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
            "messages": []
        }

        # ensure log directory exists
        if not path.exists(f"{self.chat_log_path}/chat_history/{branch_name}"):
            makedirs(f"{self.chat_log_path}/chat_history/{branch_name}")

        # create log file
        with open(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "w") as file:
            yaml.dump(log_info, file)

    def _update_log_file(self, branch_name: str, session_id: str, log_data: dict) -> None:
        """
        Updates the log file with the new log data.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged. Should contain the following keys: "user_info", "cost", "tokens", and "message".
        
        Returns:
            None
        """
        with open(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "r") as file:
            log: dict = yaml.safe_load(file)

            log["messages"] = log.get("messages", [])
            log["messages"].append(
                {
                    "role": "user",
                    "content": log_data["messages"][-2],
                })
            log["messages"].append({
                    "role": "system",
                    "content": log_data["messages"][-1],
                    "context": [context.page_content for context in log_data["retrieved_context"]],
                    "execution_time": log_data.get("execution_time", 0),
                    "tokens_used": log_data.get("tokens", 0),
                    "cost": log_data.get("cost", 0)
                })
            
            log["total_cost"] += log_data.get("cost", 0)
            log["total_tokens"] += log_data.get("tokens", 0)

        with open(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "w") as file:
            yaml.dump(log, file)

    def _does_log_exist(self, branch_name: str, session_id: str) -> bool:
        """
        Checks if a log file exists for the given session ID.

        Args:
            session_id (str): The session ID to check for.
        
        Returns:
            bool: True if the log file exists, False otherwise.
        """
        return path.exists(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log")
