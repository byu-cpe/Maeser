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