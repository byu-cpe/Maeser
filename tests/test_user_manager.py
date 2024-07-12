import unittest
from maeser.user_manager import User, GithubAuthenticator, UserManager
from unittest.mock import patch, Mock, MagicMock

class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = User('testuser', realname='Test User', requests_left=5)

    def test_is_authenticated(self):
        self.assertTrue(self.user.is_authenticated)

    def test_is_anonymous(self):
        self.assertFalse(self.user.is_anonymous)

    def test_get_id(self):
        self.assertEqual(self.user.get_id(), 'caedm.testuser')

    def test_requests_remaining(self):
        self.assertEqual(self.user.requests_remaining, 5)
        self.user.requests_remaining = 7
        self.assertEqual(self.user.requests_remaining, 7)

    def test_requests_remaining_max(self):
        self.user.requests_remaining = 15
        self.assertEqual(self.user.requests_remaining, 10)  # max_requests is 10 by default

    def test_requests_remaining_min(self):
        self.user.requests_remaining = -1
        self.assertEqual(self.user.requests_remaining, 0)

    def test_equality(self):
        user2 = User('testuser')
        self.assertEqual(self.user, user2)
        user3 = User('anotheruser')
        self.assertNotEqual(self.user, user3)

    def test_full_id_name(self):
        self.assertEqual(self.user.full_id_name, 'caedm.testuser')


class TestGithubAuthenticator(unittest.TestCase):

    def setUp(self):
        self.auth = GithubAuthenticator('fake_client_id', 'fake_client_secret', 'https://example.com/callback')

    @patch('requests.post')
    @patch('requests.get')
    def test_authenticate_success(self, mock_get, mock_post):
        mock_post.return_value = Mock(status_code=200, json=lambda: {'access_token': 'fake_token'})
        mock_get.return_value = Mock(status_code=200, json=lambda: {'login': 'testuser', 'name': 'Test User'})

        result = self.auth.authenticate({'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
        self.assertEqual(result, ('testuser', 'Test User', "b'guest'"))

    @patch('requests.post')
    def test_authenticate_fail_token_exchange(self, mock_post):
        mock_post.return_value = Mock(status_code=400)
        result = self.auth.authenticate({'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
        self.assertIsNone(result)

    @patch('requests.post')
    @patch('requests.get')
    def test_authenticate_fail_user_info(self, mock_get, mock_post):
        mock_post.return_value = Mock(status_code=200, json=lambda: {'access_token': 'fake_token'})
        mock_get.return_value = Mock(status_code=400)
        result = self.auth.authenticate({'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
        self.assertIsNone(result)

    @patch('requests.get')
    def test_fetch_user_success(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: {'login': 'testuser', 'name': 'Test User'})
        user = self.auth.fetch_user('testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user.ident, 'testuser')
        self.assertEqual(user.realname, 'Test User')

    @patch('requests.get')
    def test_fetch_user_fail(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        user = self.auth.fetch_user('unknownuser')
        self.assertIsNone(user)

    @patch('secrets.token_urlsafe')
    def test_get_auth_info(self, mock_token_urlsafe):
        # Arrange
        mock_token_urlsafe.return_value = 'fake_state'
        auth = GithubAuthenticator('fake_client_id', 'fake_client_secret', 'https://example.com/callback')

        # Act
        oauth_state, provider_url = auth.get_auth_info()

        # Assert
        self.assertEqual(oauth_state, 'fake_state')
        self.assertIn('https://github.com/login/oauth/authorize', provider_url)
        self.assertIn('client_id=fake_client_id', provider_url)
        self.assertIn('redirect_uri=https%3A%2F%2Fexample.com%2Fcallback', provider_url)
        self.assertIn('response_type=code', provider_url)
        self.assertIn('scope=user%3Aemail', provider_url)
        self.assertIn('state=fake_state', provider_url)

        # Verify that token_urlsafe was called
        mock_token_urlsafe.assert_called_once_with(16)


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.user_manager = UserManager(':memory:')

    @patch('sqlite3.connect')
    def test_db_connection(self, mock_connect):
        mock_connect.return_value = MagicMock()
        conn = self.user_manager.db_connection
        self.assertIsNotNone(conn)

    @patch('sqlite3.connect')
    def test_register_authenticator(self, mock_connect):
        mock_connect.return_value = MagicMock()
        auth = GithubAuthenticator('id', 'secret', 'https://example.com/callback')
        self.user_manager.register_authenticator('github', auth)
        self.assertIn('github', self.user_manager.authenticators)

    @patch('sqlite3.connect')
    @patch('maeser.user_manager.User')
    def test_get_user(self, mock_user, mock_connect):
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        mock_cursor = MagicMock()
        mock_db.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = ('testuser', 0, 0, 'Test User', b'guest', 5)

        mock_user_instance = MagicMock()
        mock_user_instance.ident = 'testuser'
        mock_user_instance.realname = 'Test User'
        mock_user.return_value = mock_user_instance

        user = self.user_manager.get_user('github', 'testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user.ident, 'testuser')
        self.assertEqual(user.realname, 'Test User')

    @patch('sqlite3.connect')
    @patch('maeser.user_manager.User')
    def test_authenticate(self, mock_user, mock_connect):
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        mock_cursor = MagicMock()
        mock_db.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = ('testuser', 0, 0, 'Test User', b'guest', 5)

        mock_user_instance = MagicMock()
        mock_user_instance.ident = 'testuser'
        mock_user_instance.realname = 'Test User'
        mock_user.return_value = mock_user_instance

        auth = GithubAuthenticator('id', 'secret', 'https://example.com/callback')
        self.user_manager.register_authenticator('github', auth)

        with patch.object(auth, 'authenticate', return_value=('testuser', 'Test User', b'guest')):
            user = self.user_manager.authenticate('github', {'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
            self.assertIsNotNone(user)
            self.assertEqual(user.ident, 'testuser')
            self.assertEqual(user.realname, 'Test User')

if __name__ == '__main__':
    unittest.main()
