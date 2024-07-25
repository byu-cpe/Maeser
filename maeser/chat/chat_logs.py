from maeser.user_manager import UserManager, User
from abc import ABC, abstractmethod
from datetime import datetime
import os
import yaml
from os import path, stat, walk
import subprocess

class BaseChatLogsManager(ABC):
    def __init__(self, chat_log_path: str, user_manager: UserManager | None = None) -> None:
        self.chat_log_path: str = chat_log_path
        self.user_manager: UserManager | None = user_manager

        # create log directory if it does not exist
        if not os.path.exists(self.chat_log_path):
            os.makedirs(self.chat_log_path)

    @abstractmethod
    def log(self, branch_name: str, session_id: str, log_data: dict) -> None:
        '''
        Abstract method to log chat data.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged.
        
        Returns:
            None
        '''
        pass

    @abstractmethod
    def log_feedback(self, branch_name: str, session_id: str, message_index: int, feedback: str):
        '''
        Abstract method to log feedback for a message.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            message_index (int): The index of the message to add feedback to.
            feedback (str): The feedback to add to the message.
        
        Returns:
            None
        '''
        pass

    @abstractmethod
    def get_chat_history_overview(self, user: User | None) -> list[dict]:
        '''
        Abstract method to get an overview of chat history.
        This is used to display a list of overview to previous chat conversations.

        Args:
            user (User): The user to get chat history for.

        Returns:
            list[dict]: A of dictionaries containing information about previous chat conversations. Each should have the following keys:
            - "branch": The name of the branch.
            - "session": The session ID for the conversation.
            - "modified": The timestamp of when the chat conversation was last modified.
            - "header": The text that will be used as the link text. Usually the first message in the conversation. Could also be a conversation title.
        '''
        pass

    @abstractmethod
    def get_chat_history(self, branch_name: str, session_id: str) -> dict:
        '''
        Abstract method to get chat history for a session.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
        
        Returns:
            dict: The chat history for the session.
        '''
        pass

class ChatLogsManager(BaseChatLogsManager):
    def __init__(self, chat_log_path: str) -> None:
        super().__init__(chat_log_path)

    def log(self, branch_name: str, session_id: str, log_data: dict) -> None:
        '''
        Logs chat data to a YAML file.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged. Should contain the following keys: "user", "cost", "tokens", and "message".
        
        Returns:
            None
        '''
        if not self._does_log_exist(branch_name, session_id):
            self._create_log_file(branch_name, session_id, log_data.get("user", None))
        else:
            self._update_log_file(branch_name, session_id, log_data)

    def log_feedback(self, branch_name: str, session_id: str, message_index: int, feedback: str) -> None:
        '''
        Adds feedback to the log for a specific response in a specific session.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            message_index (int): The index of the message to add feedback to.
            feedback (str): The feedback to add to the message.

        Returns:
            None
        '''
        with open(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "r") as file:
            log: dict = yaml.safe_load(file)
            log['messages'][message_index]['liked'] = feedback

        with open(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "w") as file:
            yaml.dump(log, file)

    def get_chat_history_overview(self, user: User | None) -> list[dict]:
        '''
        Gets an overview of chat history.

        Returns:
            dict: A dictionary containing information about previous chat conversations.
        '''
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

    def get_chat_history(self, branch_name: str, session_id: str) -> dict:
        '''
        Gets the chat history for a specific session in a specific branch.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.

        Returns:
            dict: The chat history for the session.
        '''
        with open(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "r") as file:
            return yaml.safe_load(file)

    def _get_file_list(self) -> list[dict]:
        """
        Get the list of chat history files with metadata.

        Returns:
            list: The list of files with their metadata.
        """
        def get_creation_time(file_path):
            result = subprocess.run(['stat', '-c', '%W', file_path], stdout=subprocess.PIPE)
            crtime = int(result.stdout)
            
            if crtime == 0:
                raise AttributeError("Creation time attribute is not available")
            
            return crtime
        
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
                    except AttributeError:
                        created_time = stat(file_path).st_ctime
                    
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
        if not os.path.exists(f"{self.chat_log_path}/chat_history/{branch_name}"):
            os.makedirs(f"{self.chat_log_path}/chat_history/{branch_name}")

        # create log file
        with open(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log", "w") as file:
            yaml.dump(log_info, file)

    def _update_log_file(self, branch_name: str, session_id: str, log_data: dict) -> None:
        '''
        Updates the log file with the new log data.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged. Should contain the following keys: "user_info", "cost", "tokens", and "message".
        
        Returns:
            None
        '''
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
        '''
        Checks if a log file exists for the given session ID.

        Args:
            session_id (str): The session ID to check for.
        
        Returns:
            bool: True if the log file exists, False otherwise.
        '''
        return os.path.exists(f"{self.chat_log_path}/chat_history/{branch_name}/{session_id}.log")