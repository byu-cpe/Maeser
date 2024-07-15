from abc import ABC, abstractmethod
from datetime import datetime
import os
import yaml

class BaseChatLogsManager(ABC):
    def __init__(self, chat_log_path: str) -> None:
        self.chat_log_path: str = chat_log_path

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

class ChatLogsManager(BaseChatLogsManager):
    def __init__(self, chat_log_path: str) -> None:
        super().__init__(chat_log_path)

    def log(self, branch_name: str, session_id: str, log_data: dict) -> None:
        '''
        Logs chat data to a YAML file.

        Args:
            branch_name (str): The name of the branch.
            session_id (str): The session ID for the conversation.
            log_data (dict): The data to be logged. Should contain the following keys: "user_info", "cost", "tokens", and "message".
        
        Returns:
            None
        '''
        if not self._does_log_exist(branch_name, session_id):
            self._create_log_file(branch_name, session_id, log_data.get("user_info", {}))
        else:
            self._update_log_file(branch_name, session_id, log_data)

    def _create_log_file(self, branch_name: str, session_id: str, user_info: dict) -> None:
        # compile log information
        log_info: dict = {
            "session_id": session_id,
            "user": user_info.get("full_id_name", "default_user"),
            "real_name": user_info.get("realname", "Default User"),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "branch": branch_name,
            "total_cost": 0,
            "total_tokens": 0,
            "messages": []
        }

        # ensure log directory exists
        if not os.path.exists(f"{self.chat_log_path}/{branch_name}"):
            os.makedirs(f"{self.chat_log_path}/{branch_name}")

        # create log file
        with open(f"{self.chat_log_path}/{branch_name}/{session_id}.log", "w") as file:
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
        with open(f"{self.chat_log_path}/{branch_name}/{session_id}.log", "r") as file:
            log: dict = yaml.safe_load(file)

            log["messages"] = log.get("messages", [])
            log["messages"].append(
                {
                    "role": "user",
                    "content": log_data.get("message", "No message provided.")
                })
            log["messages"].append({
                    "role": "system",
                    "content": log_data.get("response", "No response provided."),
                    "context": log_data.get("context", []),
                    "execution_time": log_data.get("execution_time", 0),
                    "tokens_used": log_data.get("tokens", 0),
                    "cost": log_data.get("cost", 0)
                })
            
            log["total_cost"] += log_data.get("cost", 0)
            log["total_tokens"] += log_data.get("tokens", 0)

        with open(f"{self.chat_log_path}/{branch_name}/{session_id}.log", "w") as file:
            yaml.dump(log, file)

    def _does_log_exist(self, branch_name: str, session_id: str) -> bool:
        '''
        Checks if a log file exists for the given session ID.

        Args:
            session_id (str): The session ID to check for.
        
        Returns:
            bool: True if the log file exists, False otherwise.
        '''
        return os.path.exists(f"{self.chat_log_path}/{branch_name}/{session_id}.log")