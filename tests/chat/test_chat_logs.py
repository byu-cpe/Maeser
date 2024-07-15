import pytest
import os
import yaml
from maeser.chat.chat_logs import ChatLogsManager

@pytest.fixture
def chat_logs_manager(tmp_path):
    return ChatLogsManager(str(tmp_path))

def test_create_log_file(chat_logs_manager):
    branch_name = "test_branch"
    session_id = "test_session"
    user_info = {
        "full_id_name": "test_user",
        "realname": "Test User"
    }

    chat_logs_manager._create_log_file(branch_name, session_id, user_info)

    log_path = f"{chat_logs_manager.chat_log_path}/{branch_name}/{session_id}.log"
    assert os.path.exists(log_path)

    with open(log_path, "r") as file:
        log_content = yaml.safe_load(file)

    assert log_content["session_id"] == session_id
    assert log_content["user"] == "test_user"
    assert log_content["real_name"] == "Test User"
    assert log_content["branch"] == branch_name
    assert log_content["total_cost"] == 0
    assert log_content["total_tokens"] == 0
    assert log_content["messages"] == []

def test_update_log_file(chat_logs_manager):
    branch_name = "test_branch"
    session_id = "test_session"
    user_info = {"full_id_name": "test_user", "realname": "Test User"}
    chat_logs_manager._create_log_file(branch_name, session_id, user_info)

    log_data = {
        "message": "Test message",
        "response": "Test response",
        "context": ["context1", "context2"],
        "execution_time": 1.5,
        "tokens": 100,
        "cost": 0.002
    }

    chat_logs_manager._update_log_file(branch_name, session_id, log_data)

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

def test_does_log_exist(chat_logs_manager):
    branch_name = "test_branch"
    session_id = "test_session"
    user_info = {"full_id_name": "test_user", "realname": "Test User"}

    assert not chat_logs_manager._does_log_exist(branch_name, session_id)

    chat_logs_manager._create_log_file(branch_name, session_id, user_info)

    assert chat_logs_manager._does_log_exist(branch_name, session_id)

def test_log_feedback(chat_logs_manager):
    branch_name = "test_branch"
    session_id = "test_session"
    initial_log_data = {
        "user_info": {"full_id_name": "test_user", "realname": "Test User"},
        "message": "Test message",
        "response": "Test response",
        "context": ["context1"],
        "execution_time": 1.0,
        "tokens": 50,
        "cost": 0.001
    }
    chat_logs_manager.log(branch_name, session_id, initial_log_data)

    # Add message to log
    chat_logs_manager._update_log_file(branch_name, session_id, {
        "message": "Test message",
        "response": "Test response",
        "context": ["context1"],
        "execution_time": 1.0,
        "tokens": 50,
        "cost": 0.001
    })

    # Test adding positive feedback
    chat_logs_manager.log_feedback(branch_name, session_id, 1, True)

    log_path = f"{chat_logs_manager.chat_log_path}/{branch_name}/{session_id}.log"
    with open(log_path, "r") as file:
        log_content = yaml.safe_load(file)

    assert log_content["messages"][1]["liked"] == True

    # Test adding negative feedback
    chat_logs_manager.log_feedback(branch_name, session_id, 1, False)

    with open(log_path, "r") as file:
        log_content = yaml.safe_load(file)

    assert log_content["messages"][1]["liked"] == False

def test_log_feedback_invalid_index(chat_logs_manager):
    branch_name = "test_branch"
    session_id = "test_session"
    initial_log_data = {
        "user_info": {"full_id_name": "test_user", "realname": "Test User"},
        "message": "Test message",
        "response": "Test response",
    }
    chat_logs_manager.log(branch_name, session_id, initial_log_data)

    with pytest.raises(IndexError):
        chat_logs_manager.log_feedback(branch_name, session_id, 5, "positive")

def test_get_chat_history(chat_logs_manager):
    branch_name = "test_branch"
    session_id = "test_session"
    initial_log_data = {
        "user_info": {"full_id_name": "test_user", "realname": "Test User"},
        "message": "Test message",
        "response": "Test response",
        "context": ["context1"],
        "execution_time": 1.0,
        "tokens": 50,
        "cost": 0.001
    }
    chat_logs_manager.log(branch_name, session_id, initial_log_data)

    # Add messages to log
    chat_logs_manager._update_log_file(branch_name, session_id, {
        "message": "Test message",
        "response": "Test response",
        "context": ["context1"],
        "execution_time": 1.0,
        "tokens": 50,
        "cost": 0.001
    })

    chat_history = chat_logs_manager.get_chat_history(branch_name, session_id)

    assert chat_history["session_id"] == session_id
    assert chat_history["user"] == "test_user"
    assert chat_history["real_name"] == "Test User"
    assert chat_history["branch"] == branch_name
    assert len(chat_history["messages"]) == 2
    assert chat_history["total_cost"] == 0.001
    assert chat_history["total_tokens"] == 50

def test_get_chat_history_nonexistent(chat_logs_manager):
    branch_name = "nonexistent_branch"
    session_id = "nonexistent_session"

    with pytest.raises(FileNotFoundError):
        chat_logs_manager.get_chat_history(branch_name, session_id)
