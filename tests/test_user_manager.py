"""
© 2024 Carson Bush

This file is part of the Maeser unit test suite.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
import pytest
from maeser.user_manager import UserManager, GithubAuthenticator

@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Fixture to provide a temporary database file path."""
    return tmp_path / "test_db.sqlite"

@pytest.fixture
def user_manager(db_path: Path) -> UserManager:
    """Fixture to create a UserManager instance."""
    um = UserManager(str(db_path))
    um.register_authenticator("github", GithubAuthenticator("test_id", "test_secret", "http://localhost/callback"))
    
    # Ensure the table for GitHub users exists
    with um.db_connection as db:
        db.execute('''CREATE TABLE IF NOT EXISTS githubUsers (
                        user_id TEXT PRIMARY KEY,
                        blacklisted BOOLEAN NOT NULL CHECK (blacklisted IN (0, 1)),
                        admin BOOLEAN NOT NULL CHECK (admin IN (0, 1)),
                        realname TEXT,
                        usertype TEXT NOT NULL,
                        requests_left INTEGER NOT NULL)''')
    return um

@pytest.fixture
def github_authenticator() -> GithubAuthenticator:
    """Fixture to create a GithubAuthenticator instance."""
    return GithubAuthenticator(client_id="test_id", client_secret="test_secret", auth_callback_uri="http://localhost/callback")

def test_register_authenticator(user_manager: UserManager, github_authenticator: GithubAuthenticator):
    """Test registering an authenticator."""
    user_manager.register_authenticator("github", github_authenticator)
    assert "github" in user_manager.authenticators

def test_get_user_not_found(user_manager: UserManager):
    """Test retrieving a user that does not exist."""
    user = user_manager.get_user("github", "non_existent_user")
    assert user is None

def test_create_and_get_user(user_manager: UserManager, github_authenticator: GithubAuthenticator):
    """Test creating and retrieving a user."""
    user_manager.register_authenticator("github", github_authenticator)
    user_manager._create_or_update_user("github", "test_user", "Test User", "guest")
    user = user_manager.get_user("github", "test_user")
    assert user is not None
    assert user.ident == "test_user"
    assert user.realname == "Test User"

def test_update_admin_status(user_manager: UserManager, github_authenticator: GithubAuthenticator) -> None:
    """Test updating the admin status of a user."""
    user_manager.register_authenticator("github", github_authenticator)
    user_manager._create_or_update_user("github", "test_user", "Test User", "guest")
    user_manager.update_admin_status("github", "test_user", True)
    user = user_manager.get_user("github", "test_user")
    assert user is not None
    assert user.admin is True

def test_update_banned_status(user_manager: UserManager, github_authenticator: GithubAuthenticator):
    """Test updating the banned status of a user."""
    user_manager.register_authenticator("github", github_authenticator)
    user_manager._create_or_update_user("github", "test_user", "Test User", "guest")
    user_manager.update_banned_status("github", "test_user", True)
    user = user_manager.get_user("github", "test_user")
    assert user is not None
    assert user.is_active is False

def test_refresh_requests(user_manager: UserManager, github_authenticator: GithubAuthenticator):
    """Test refreshing requests for all users."""
    user_manager.register_authenticator("github", github_authenticator)
    user_manager._create_or_update_user("github", "test_user1", "Test User 1", "guest")
    user_manager._create_or_update_user("github", "test_user2", "Test User 2", "guest")
    user_manager.refresh_requests(5)
    user1 = user_manager.get_user("github", "test_user1")
    user2 = user_manager.get_user("github", "test_user2")
    assert user1 is not None
    assert user2 is not None
    assert user1.requests_remaining == 10
    assert user2.requests_remaining == 10

def test_decrease_requests(user_manager: UserManager, github_authenticator: GithubAuthenticator):
    """Test decreasing the number of requests remaining for a user."""
    user_manager.register_authenticator("github", github_authenticator)
    user_manager._create_or_update_user("github", "test_user", "Test User", "guest")
    user_manager.decrease_requests("github", "test_user", 3)
    user = user_manager.get_user("github", "test_user")
    assert user is not None
    assert user.requests_remaining == 7

def test_increase_requests(user_manager: UserManager, github_authenticator: GithubAuthenticator):
    """Test increasing the number of requests remaining for a user."""
    user_manager.register_authenticator("github", github_authenticator)
    user_manager._create_or_update_user("github", "test_user", "Test User", "guest")
    user_manager.decrease_requests("github", "test_user", 3)
    user_manager.increase_requests("github", "test_user", 2)
    user = user_manager.get_user("github", "test_user")
    assert user is not None
    assert user.requests_remaining == 9

def test_get_requests_remaining(user_manager: UserManager, github_authenticator: GithubAuthenticator):
    """Test getting the number of requests remaining for a user."""
    user_manager.register_authenticator("github", github_authenticator)
    user_manager._create_or_update_user("github", "test_user", "Test User", "guest")
    remaining_requests = user_manager.get_requests_remaining("github", "test_user")
    assert remaining_requests == 10
