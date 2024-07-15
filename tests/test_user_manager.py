import pytest
from pytest_mock import mocker
from maeser.user_manager import User, GithubAuthenticator, UserManager, BaseAuthenticator

@pytest.fixture
def user() -> User:
    return User('testuser', realname='Test User', requests_left=5)

@pytest.fixture
def github_auth() -> GithubAuthenticator:
    return GithubAuthenticator('fake_client_id', 'fake_client_secret', 'https://example.com/callback')

@pytest.fixture
def user_manager() -> UserManager:
    return UserManager(':memory:')

# Mock database fixture with context management
@pytest.fixture
def mock_db(mocker):
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mocker.patch('sqlite3.connect', return_value=mock_db)
    return mock_db

# User tests
def test_is_authenticated(user: User):
    assert user.is_authenticated

def test_is_anonymous(user: User):
    assert not user.is_anonymous

def test_get_id(user: User):
    assert user.get_id() == 'caedm.testuser'

def test_requests_remaining(user: User):
    assert user.requests_remaining == 5
    user.requests_remaining = 7
    assert user.requests_remaining == 7

def test_requests_remaining_max(user: User):
    user.requests_remaining = 15
    assert user.requests_remaining == 10  # max_requests is 10 by default

def test_requests_remaining_min(user: User):
    user.requests_remaining = -1
    assert user.requests_remaining == 0

def test_equality(user: User):
    user2 = User('testuser')
    assert user == user2
    user3 = User('anotheruser')
    assert user != user3

def test_full_id_name(user: User):
    assert user.full_id_name == 'caedm.testuser'

def test_user_init_with_custom_values():
    custom_user = User('customuser', blacklisted=True, admin=True, realname='Custom User', 
                       usergroup='b\'admin\'', authmethod='custom', requests_left=20, 
                       max_requests=30, aka={'nickname': 'custom'})
    assert custom_user.ident == 'customuser'
    assert not custom_user.is_active
    assert custom_user.admin
    assert custom_user.realname == 'Custom User'
    assert custom_user.usergroup == 'b\'admin\''
    assert custom_user.auth_method == 'custom'
    assert custom_user.requests_remaining == 20
    assert custom_user.aka == {'nickname': 'custom'}

# GithubAuthenticator tests
def test_authenticate_success(github_auth: GithubAuthenticator, mocker):
    mock_post = mocker.patch('requests.post', return_value=mocker.Mock(status_code=200, json=lambda: {'access_token': 'fake_token'}))
    mock_get = mocker.patch('requests.get', return_value=mocker.Mock(status_code=200, json=lambda: {'login': 'testuser', 'name': 'Test User'}))

    result = github_auth.authenticate({'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
    assert result == ('testuser', 'Test User', "b'guest'")
    mock_post.assert_called_once()
    mock_get.assert_called_once()

def test_authenticate_fail_token_exchange(github_auth: GithubAuthenticator, mocker):
    mocker.patch('requests.post', return_value=mocker.Mock(status_code=400))
    result = github_auth.authenticate({'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
    assert result is None

def test_authenticate_fail_user_info(github_auth: GithubAuthenticator, mocker):
    mocker.patch('requests.post', return_value=mocker.Mock(status_code=200, json=lambda: {'access_token': 'fake_token'}))
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=400))
    result = github_auth.authenticate({'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
    assert result is None

def test_fetch_user_success(github_auth: GithubAuthenticator, mocker):
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=200, json=lambda: {'login': 'testuser', 'name': 'Test User'}))
    user = github_auth.fetch_user('testuser')
    assert user is not None
    assert user.ident == 'testuser'
    assert user.realname == 'Test User'

def test_fetch_user_fail(github_auth: GithubAuthenticator, mocker):
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=404))
    user = github_auth.fetch_user('unknownuser')
    assert user is None

def test_get_auth_info(github_auth: GithubAuthenticator, mocker):
    mocker.patch('secrets.token_urlsafe', return_value='fake_state')
    oauth_state, provider_url = github_auth.get_auth_info()
    assert oauth_state == 'fake_state'
    assert 'https://github.com/login/oauth/authorize' in provider_url
    assert 'client_id=fake_client_id' in provider_url
    assert 'redirect_uri=https%3A%2F%2Fexample.com%2Fcallback' in provider_url
    assert 'response_type=code' in provider_url
    assert 'scope=user%3Aemail' in provider_url
    assert 'state=fake_state' in provider_url

def test_str_representation(github_auth: GithubAuthenticator):
    assert str(github_auth) == 'GithubAuthenticator'

# UserManager tests
def test_register_authenticator(user_manager: UserManager):
    auth = GithubAuthenticator('id', 'secret', 'https://example.com/callback')
    user_manager.register_authenticator('github', auth)
    assert 'github' in user_manager.authenticators

def test_register_authenticator_invalid_name(user_manager: UserManager):
    auth = GithubAuthenticator('id', 'secret', 'https://example.com/callback')
    with pytest.raises(ValueError):
        user_manager.register_authenticator('invalid name', auth)

def test_get_user(user_manager: UserManager, mock_db, mocker):
    mock_cursor = mocker.Mock()
    mock_db.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ('testuser', 0, 0, 'Test User', b'guest', 5)

    user_manager.register_authenticator('github', mocker.Mock())
    user = user_manager.get_user('github', 'testuser')
    assert user is not None
    assert user.ident == 'testuser'
    assert user.realname == 'Test User'

def test_get_user_not_found(user_manager: UserManager, mock_db, mocker):
    mock_cursor = mocker.Mock()
    mock_db.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    user_manager.register_authenticator('github', mocker.Mock())
    user = user_manager.get_user('github', 'unknownuser')
    assert user is None

def test_authenticate(user_manager: UserManager, mock_db, mocker):
    mock_cursor = mocker.Mock()
    mock_db.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ('testuser', 0, 0, 'Test User', b'guest', 5)

    mock_auth = mocker.Mock(spec=BaseAuthenticator)
    mock_auth.authenticate.return_value = ('testuser', 'Test User', b'guest')
    user_manager.register_authenticator('github', mock_auth)

    user = user_manager.authenticate('github', {'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
    assert user is not None
    assert user.ident == 'testuser'
    assert user.realname == 'Test User'

def test_authenticate_fail(user_manager: UserManager, mocker):
    mock_auth = mocker.Mock(spec=BaseAuthenticator)
    mock_auth.authenticate.return_value = None
    user_manager.register_authenticator('github', mock_auth)

    user = user_manager.authenticate('github', {'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
    assert user is None

def test_update_admin_status(user_manager: UserManager, mock_db, mocker):
    user_manager.register_authenticator('github', mocker.Mock())
    user_manager.update_admin_status('github', 'testuser', True)
    mock_db.execute.assert_called_once()

def test_update_banned_status(user_manager: UserManager, mock_db, mocker):
    user_manager.register_authenticator('github', mocker.Mock())
    user_manager.update_banned_status('github', 'testuser', True)
    mock_db.execute.assert_called_once()

def test_refresh_requests(user_manager: UserManager, mock_db, mocker):
    user_manager.register_authenticator('github', mocker.Mock())
    user_manager.refresh_requests(2)
    mock_db.execute.assert_called_once()

@pytest.mark.parametrize("method,expected_calls", [
    ("decrease_requests", 1),
    ("increase_requests", 1),
    ("get_requests_remaining", 1)
])
def test_request_operations(user_manager: UserManager, mock_db, mocker, method, expected_calls):
    user_manager.register_authenticator('github', mocker.Mock())
    getattr(user_manager, method)('github', 'testuser')
    assert mock_db.execute.call_count == expected_calls
