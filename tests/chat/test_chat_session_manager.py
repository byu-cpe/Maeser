import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID
from datetime import datetime
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.chat.chat_logs import BaseChatLogsManager
from maeser.user_manager import User
from langgraph.graph import StateGraph

@pytest.fixture
def chat_logs_manager_mock():
    return MagicMock(spec=BaseChatLogsManager)

@pytest.fixture
def state_graph_mock():
    mock = MagicMock(spec=StateGraph)
    mock.invoke = MagicMock(return_value={"response": "Test response"})
    return mock

@pytest.fixture
def chat_session_manager(chat_logs_manager_mock, state_graph_mock):
    manager = ChatSessionManager(chat_logs_manager=chat_logs_manager_mock)
    manager.graphs["test_branch"] = {"graph": state_graph_mock}
    return manager

@pytest.fixture
def mock_user():
    return User("test_user")

def test_register_branch(chat_session_manager, state_graph_mock):
    chat_session_manager.register_branch("test_branch", "Test Branch", state_graph_mock)
    assert "test_branch" in chat_session_manager.graphs
    assert chat_session_manager.graphs["test_branch"]["label"] == "Test Branch"
    assert chat_session_manager.graphs["test_branch"]["graph"] == state_graph_mock

def test_get_new_session_id_with_user(chat_session_manager, mock_user):
    session_id = chat_session_manager.get_new_session_id("test_branch", mock_user)
    assert f"{mock_user.auth_method}-{mock_user.ident}" in session_id
    chat_session_manager.chat_logs_manager.log.assert_called_once_with("test_branch", session_id, {mock_user: mock_user})

def test_get_new_session_id_without_user(chat_session_manager):
    session_id = chat_session_manager.get_new_session_id("test_branch")
    assert "anon" in session_id
    chat_session_manager.chat_logs_manager.log.assert_called_once_with("test_branch", session_id, {None: None})

@patch('maeser.chat.chat_session_manager.get_openai_callback')
@patch('maeser.chat.chat_session_manager.time')
def test_ask_question(mock_time, mock_get_openai_callback, chat_session_manager, state_graph_mock):
    mock_time.time.side_effect = [0, 1]  # Start time and end time
    mock_callback = MagicMock()
    mock_callback.total_tokens = 100
    mock_callback.total_cost = 0.002
    mock_get_openai_callback.return_value.__enter__.return_value = mock_callback

    response = chat_session_manager.ask_question("Test question", "test_branch", "test_session_id")

    assert response == {
        "response": "Test response",
        "tokens_used": 100,
        "cost": 0.002,
        "execution_time": 1
    }
    state_graph_mock.invoke.assert_called_once_with(
        {"messages": ["Test question"]},
        config={"configurable": {"thread_id": "test_session_id"}}
    )
    chat_session_manager.chat_logs_manager.log.assert_called_once_with("test_branch", "test_session_id", response)

def test_add_feedback(chat_session_manager):
    chat_session_manager.add_feedback("test_branch", "test_session_id", 1, "Great response!")
    chat_session_manager.chat_logs_manager.log_feedback.assert_called_once_with(
        "test_branch", "test_session_id", 1, "Great response!"
    )

def test_get_conversation_history(chat_session_manager):
    chat_session_manager.chat_logs_manager.get_chat_history.return_value = {"history": "test history"}
    history = chat_session_manager.get_conversation_history("test_branch", "test_session_id")
    assert history == {"history": "test history"}
    chat_session_manager.chat_logs_manager.get_chat_history.assert_called_once_with("test_branch", "test_session_id")

def test_get_conversation_history_no_chat_logs_manager():
    chat_session_manager = ChatSessionManager()
    history = chat_session_manager.get_conversation_history("test_branch", "test_session_id")
    assert history == {}