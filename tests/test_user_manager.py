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
        self.auth = GithubAuthenticator('fake_client_id', 'fake_client_secret')

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
        auth = GithubAuthenticator('id', 'secret')
        self.user_manager.register_authenticator('github', auth)
        self.assertIn('github', self.user_manager.authenticators)

    @patch('sqlite3.connect')
    def test_get_user(self, mock_connect):
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.execute().fetchone.return_value = ('testuser', False, False, 'Test User', "b'guest'", 5)

        user = self.user_manager.get_user('github', 'testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user.ident, 'testuser')
        self.assertEqual(user.realname, 'Test User')

    @patch('sqlite3.connect')
    def test_authenticate(self, mock_connect):
        mock_connect.return_value = MagicMock()
        auth = GithubAuthenticator('id', 'secret')
        self.user_manager.register_authenticator('github', auth)

        with patch.object(auth, 'authenticate', return_value=('testuser', 'Test User', "b'guest'")):
            user = self.user_manager.authenticate('github', {'code': 'fake_code', 'state': 'fake_state'}, 'fake_state')
            self.assertIsNotNone(user)
            self.assertEqual(user.ident, 'testuser')

if __name__ == '__main__':
    unittest.main()
