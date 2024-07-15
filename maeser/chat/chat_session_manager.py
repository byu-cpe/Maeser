from datetime import datetime
import os
import yaml
import time
from uuid import uuid4 as uid
from langchain_community.callbacks import get_openai_callback
from langgraph.graph import StateGraph

class ChatSessionManager:
    """
    Manages and directs sessions for multiple chat interfaces.
    """
    
    def __init__(
        self,
        log_path: str
    ) -> None:
        """
        Initializes the ChatSessionManager with given directories, model, and chat branches.

        Args:
            llm_model (str): The language model to be used.
            chat_branches (list): A list of chat branches with their actions.
            log_path (str): Path where logs are to be stored.

        Returns:
            None
        """
        self.log_path: str = log_path
        self.graphs: dict = {}

    def register_branch(self, branch_name: str, branch_label: str, graph: StateGraph) -> None:
        """
        Registers a branch with its information and graph.

        Args:
            branch_name (str): The name of the branch.
            branch_label (str): The label of the branch.
            graph (StateGraph): The graph for the branch.
        
        Returns:
            None
        """
        self.graphs[branch_name] = {
            "label": branch_label,
            "graph": graph
        }

    def _create_log_file(self, path: str, branch_name: str, user_info: dict, session_id: str) -> None:
        """
        Creates a log file at the given path.

        Args:
            path (str): The path to create the log file at.
            branch_name (str): The action of the branch to create the log file for.
            user_info (dict): The user information for the session.
            session_id (str): The session ID for the conversation.

        Returns:
            None
        """
        # create log directory if it does not exist
        if not os.path.exists(path):
            os.makedirs(path)

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

        # create log file
        with open(f"{path}/{session_id}.log", "w") as file:
            yaml.dump(log_info, file)

    def get_new_session_id(self, branch_name: str, user_info: dict) -> str:
        """
        Creates a new chat session for the given branch action.
        Includes creating a new log file for the session.

        Args:
            branch_name (str): The action of the branch to create a session for.
            user_info (dict): The user information for the session.

        Returns:
            str: The session ID for the new session.
        """
        # generate session ID
        session_id: str = str(uid())

        # create log file
        log_branch_path: str = self.log_path + '/chat_history/' + branch_name
        self._create_log_file(log_branch_path, branch_name, user_info, session_id)

        return session_id
    
    def ask_question(self, message: str, branch_name: str, sess_id: str) -> dict:
        """
        Asks a question in a specific session of a branch.

        Args:
            message (str): The question to ask.
            branch_name (str): The action of the branch to ask the question in.
            sess_id (str): The session ID to ask the question in.

        Returns:
            dict: The response to the question.
        """
        config = {"configurable": {"thread_id": sess_id}}
        start_time = time.time()
        # get token count for the response
        with get_openai_callback() as cb:
            response = self.graphs[branch_name].invoke({
                "messages": [message],
            }, config=config)
            response["tokens_used"] = cb.total_tokens
            response["cost"] = cb.total_cost
        end_time = time.time()
        execution_time = end_time - start_time

        response["execution_time"] = execution_time
        self._update_log(branch_name, sess_id, response)
        return response
    
    def add_feedback_to_log(self, branch_name: str, session_id: str, message_index: int, feedback: str) -> None:
        """
        Adds feedback to the log for a specific response in a specific session.

        Args:
            session_id (str): The session ID for the conversation.
            message_index (int): The index of the message to add feedback to.
            feedback (str): The feedback to add to the message.
        
        Returns:
            None
        """
        log_branch_path = self.log_path + '/chat_history/' + branch_name
        filename = f"{session_id}.log"

        with open(f"{log_branch_path}/{filename}", "r") as file:
            log = yaml.safe_load(file)
            log['messages'][message_index]['liked'] = feedback

        with open(f"{log_branch_path}/{filename}", "w") as file:
            yaml.dump(log, file)

    def get_conversation_history(self, branch_name: str, session_id: str) -> dict:
        """
        Gets the conversation history for a specific session in a specific branch.

        Args:
            branch_name (str): The action of the branch to get the conversation history from.
            session_id (str): The session ID to get the conversation history from.

        Returns:
            dict: The conversation history for the session.
        """
        log_branch_path = self.log_path + '/chat_history/' + branch_name
        filename = f"{session_id}.log"

        with open(f"{log_branch_path}/{filename}", "r") as file:
            return yaml.safe_load(file)

    def _update_log(self, branch_name: str, session_id: str, response: dict) -> None:
        """
        Updates the log with the response to the question.

        Args:
            branch_name (str): The action of the branch to update the log for.
            session_id (str): The session ID for the conversation.
            response (dict): The response to the question.

        Returns:
            None
        """
        def get_context():
            try:
                return [{"content": document.page_content, "metadata": document.metadata} for document in response["retrieved_context"]]
            except KeyError:
                return []
        
        log_branch_path = self.log_path + '/chat_history/' + branch_name
            
        filename = f"{session_id}.log"

        with open(f"{log_branch_path}/{filename}", "r") as file:
            log = yaml.safe_load(file)

            log["messages"] = log.get("messages", [])
            log["messages"].append(
                {
                    "role": "user",
                    "content": response["messages"][-2]
                })
            log["messages"].append({
                    "role": "system",
                    "content": response["messages"][-1],
                    "context": get_context(),
                    "execution_time": response["execution_time"],
                    "tokens_used": response["tokens_used"],
                    "cost": response["cost"]
                })
            
            log["total_cost"] += response["cost"]
            log["total_tokens"] += response["tokens_used"]

        with open(f"{log_branch_path}/{filename}", "w") as file:
            yaml.dump(log, file)