import pytest
import os
import yaml
from maeser.chat.chat_logs import ChatLogsManager
from maeser.user_manager import User

@pytest.fixture
def chat_logs_manager(tmp_path):
    return ChatLogsManager(str(tmp_path))

@pytest.fixture
def mock_user():
    return User("test_user")

@pytest.fixture
def test_log_data():
    return {
        "message": "Test message",
        "response": "Test response",
        "context": ["context1", "context2"],
        "execution_time": 1.5,
        "tokens": 100,
        "cost": 0.002
    }

@pytest.fixture
def create_test_log(chat_logs_manager, mock_user):
    def _create_log(branch_name, session_id, log_data=None):
        chat_logs_manager._create_log_file(branch_name, session_id, mock_user)
        if log_data:
            chat_logs_manager._update_log_file(branch_name, session_id, log_data)
    return _create_log

def test_create_log_file(chat_logs_manager, mock_user, create_test_log):
    branch_name, session_id = "test_branch", "test_session"
    create_test_log(branch_name, session_id)

    log_path = f"{chat_logs_manager.chat_log_path}/{branch_name}/{session_id}.log"
    assert os.path.exists(log_path)

    with open(log_path, "r") as file:
        log_content = yaml.safe_load(file)

    assert log_content["session_id"] == session_id
    assert log_content["user"] == "caedm.test_user"
    assert log_content["real_name"] == "Student"
    assert log_content["branch"] == branch_name
    assert log_content["total_cost"] == 0
    assert log_content["total_tokens"] == 0
    assert log_content["messages"] == []

def test_update_log_file(chat_logs_manager, create_test_log, test_log_data):
    branch_name, session_id = "test_branch", "test_session"
    create_test_log(branch_name, session_id, test_log_data)

    log_path = f"{chat_logs_manager.chat_log_path}/{branch_name}/{session_id}.log"
    with open(log_path, "r") as file:
        log_content = yaml.safe_load(file)

    assert len(log_content["messages"]) == 2
    assert log_content["messages"][0]["role"] == "user"
    assert log_content["messages"][0]["content"] == "Test message"
    assert log_content["messages"][1]["role"] == "system"
    assert log_content["messages"][1]["content"] == "Test response"
    assert log_content["messages"][1]["context"] == ["context1", "context2"]
    assert log_content["messages"][1]["execution_time"] == 1.5
    assert log_content["messages"][1]["tokens_used"] == 100
    assert log_content["messages"][1]["cost"] == 0.002
    assert log_content["total_cost"] == 0.002
    assert log_content["total_tokens"] == 100

def test_does_log_exist(chat_logs_manager, create_test_log):
    branch_name, session_id = "test_branch", "test_session"
    assert not chat_logs_manager._does_log_exist(branch_name, session_id)

    create_test_log(branch_name, session_id)
    assert chat_logs_manager._does_log_exist(branch_name, session_id)

def test_log(chat_logs_manager, mock_user, test_log_data):
    branch_name, session_id = "test_branch", "test_session"
    initial_log_data = {**test_log_data, "user": mock_user}

    chat_logs_manager.log(branch_name, session_id, initial_log_data)
    chat_logs_manager.log(branch_name, session_id, test_log_data)

    log_path = f"{chat_logs_manager.chat_log_path}/{branch_name}/{session_id}.log"
    assert os.path.exists(log_path)

    with open(log_path, "r") as file:
        log_content = yaml.safe_load(file)

    assert log_content["user"] == "caedm.test_user"
    assert log_content["real_name"] == "Student"
    assert len(log_content["messages"]) == 2
    assert log_content["total_cost"] == 0.002
    assert log_content["total_tokens"] == 100

def test_log_feedback(chat_logs_manager, create_test_log, test_log_data):
    branch_name, session_id = "test_branch", "test_session"
    create_test_log(branch_name, session_id, test_log_data)

    chat_logs_manager.log_feedback(branch_name, session_id, 1, True)
    log_content = _read_log_file(chat_logs_manager, branch_name, session_id)
    assert log_content["messages"][1]["liked"] == True

    chat_logs_manager.log_feedback(branch_name, session_id, 1, False)
    log_content = _read_log_file(chat_logs_manager, branch_name, session_id)
    assert log_content["messages"][1]["liked"] == False

def test_log_feedback_invalid_index(chat_logs_manager, create_test_log, test_log_data):
    branch_name, session_id = "test_branch", "test_session"
    create_test_log(branch_name, session_id, test_log_data)

    with pytest.raises(IndexError):
        chat_logs_manager.log_feedback(branch_name, session_id, 5, True)

def test_get_chat_history(chat_logs_manager, create_test_log, test_log_data):
    branch_name, session_id = "test_branch", "test_session"
    create_test_log(branch_name, session_id, test_log_data)

    chat_history = chat_logs_manager.get_chat_history(branch_name, session_id)

    assert chat_history["session_id"] == session_id
    assert chat_history["user"] == "caedm.test_user"
    assert chat_history["real_name"] == "Student"
    assert chat_history["branch"] == branch_name
    assert len(chat_history["messages"]) == 2
    assert chat_history["total_cost"] == 0.002
    assert chat_history["total_tokens"] == 100

def test_get_chat_history_nonexistent(chat_logs_manager):
    with pytest.raises(FileNotFoundError):
        chat_logs_manager.get_chat_history("nonexistent_branch", "nonexistent_session")

def test_log_with_default_user(chat_logs_manager, create_test_log, test_log_data):
    branch_name, session_id = "test_branch", "test_session"
    create_test_log(branch_name, session_id, test_log_data)

    log_content = _read_log_file(chat_logs_manager, branch_name, session_id)

    assert log_content["user"] == "caedm.test_user"
    assert log_content["real_name"] == "Student"
    assert len(log_content["messages"]) == 2
    assert log_content["total_cost"] == 0.002
    assert log_content["total_tokens"] == 100

def _read_log_file(chat_logs_manager, branch_name, session_id):
    log_path = f"{chat_logs_manager.chat_log_path}/{branch_name}/{session_id}.log"
    with open(log_path, "r") as file:
        return yaml.safe_load(file)