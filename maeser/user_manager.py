import sqlite3
from typing import Union, Dict, Any
import requests
from abc import ABC, abstractmethod

try:
    from flask import url_for
except ImportError:
    def url_for(*args, **kwargs):
        raise NotImplementedError('Flask was not actually imported when this function was accessed.\nDid you follow the installation?')

class User:
    """
    This provides default implementations for the methods that Flask-Login expects user objects to have.
    """

    # Python 3 implicitly sets __hash__ to None if we override __eq__
    # We set it back to its default implementation
    __hash__ = object.__hash__

    def __init__(self, ident, blacklisted=False, admin=False, realname='Student', usergroup='b\'guest\'', authmethod='caedm', requests_left=10, max_requests=10, aka=dict()):
        self.ident = ident
        self.is_active = not blacklisted
        self.admin = admin
        self.realname = realname
        self.usergroup = usergroup
        self.auth_method = authmethod
        self._requests_remaining = requests_left
        self._max_requests = max_requests
        self.aka = aka

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.is_active

    @property
    def is_anonymous(self):
        """Return False, as anonymous users are not supported."""
        return False

    def get_id(self):
        """Return the user's full identifier name including authentication method."""
        return self.full_id_name

    @property
    def full_id_name(self):
        """Return the user's full identifier name including authentication method."""
        return f'{self.auth_method}.{self.ident}'
    @property
    def requests_remaining(self):
        return self._requests_remaining
    
    @requests_remaining.setter
    def requests_remaining(self, num: int):
        if num >= self._max_requests:
            self._requests_remaining = self._max_requests
        elif num <= 0:
            self._requests_remaining = 0
        else:
            self._requests_remaining = num

    def __eq__(self, other):
        """
        Check the equality of two User objects using get_id.

        Args:
            other (User): The other user to compare.

        Returns:
            bool: True if the users are equal, False otherwise.
        """
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Check the inequality of two User objects using get_id.

        Args:
            other (User): The other user to compare.

        Returns:
            bool: True if the users are not equal, False otherwise.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

class BaseAuthenticator(ABC):
    @abstractmethod
    def authenticate(self, *args: Any, **kwargs: Any) -> Union[tuple, None]:
        pass

    @abstractmethod
    def fetch_user(self, ident: str) -> Union[User, None]:
        pass

class GithubAuthenticator(BaseAuthenticator):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate(self, request_args: dict, oauth_state: str) -> Union[tuple, None]:
        if request_args['state'] != oauth_state or 'code' not in request_args:
            return None

        token_url = 'https://github.com/login/oauth/access_token'
        user_info_url = 'https://api.github.com/user'

        # exchange the authorization code for an access token
        response = requests.post(token_url, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': request_args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('github_auth_callback', _external=True),
        }, headers={'Accept': 'application/json'})

        if response.status_code != 200:
            print(f'GitHub authentication failed during token exchange: {response.status_code}', 'ERROR')
            return None

        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            print('GitHub authentication failed: No access token received', 'ERROR')
            return None

        response = requests.get(user_info_url, headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })

        if response.status_code != 200:
            print(f'GitHub authentication failed when fetching user info: {response.status_code}', 'ERROR')
            return None

        json_response = response.json()
        return json_response['login'], json_response['name'], 'b\'guest\''

    def fetch_user(self, username: str) -> Union[User, None]:
        user_info_url = f'https://api.github.com/users/{username}'
        response = requests.get(user_info_url)
        if response.status_code == 200:
            json_response = response.json()
            return User(json_response['login'], realname=json_response.get('name', ''), usergroup='b\'guest\'', authmethod='github')
        print(f'No GitHub user "{username}" found', "WARNING")
        return None

class UserManager:
    def __init__(self, db_file_path: str, max_requests: int = 10):
        self.db_file_path = db_file_path
        self.authenticators: Dict[str, BaseAuthenticator] = {}
        self.max_requests = max_requests
        self._create_tables()

    def register_authenticator(self, name: str, authenticator: BaseAuthenticator):
        self.authenticators[name] = authenticator
        self._create_table(name)

    @property
    def db_connection(self) -> sqlite3.Connection:
        try:
            return sqlite3.connect(self.db_file_path)
        except sqlite3.OperationalError as e:
            print(f'Unable to open sqlite db, using tempory storage: {e}')
            return sqlite3.connect(':memory:')

    def _create_tables(self):
        for auth_method in self.authenticators.keys():
            self._create_table(auth_method)

    def _create_table(self, auth_method: str):
        if not auth_method.isalnum():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            db.execute(f'''
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    user_id TEXT PRIMARY KEY,
                    blacklisted BOOL,
                    admin BOOL,
                    realname TEXT,
                    usertype TEXT,
                    requests_left INT,
                    aka TEXT
                )
            ''')

    def get_user(self, auth_method: str, ident: str) -> Union[User, None]:
        if not auth_method.isalnum():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            cursor = db.execute(
                f'SELECT user_id, blacklisted, admin, realname, usertype, requests_left FROM "{table_name}" WHERE user_id=?',
                (ident,)
            )
            row = cursor.fetchone()
            if row:
                return User(row[0], bool(row[1]), bool(row[2]), realname=row[3], usergroup=str(row[4]), requests_left=row[5], authmethod=auth_method)
        return None

    def authenticate(self, auth_method: str, *args: Any, **kwargs: Any) -> Union[User, None]:
        authenticator = self.authenticators.get(auth_method)
        if not authenticator:
            raise ValueError(f"Unsupported authentication method: {auth_method}")

        auth_result = authenticator.authenticate(*args, **kwargs)
        if auth_result:
            user_id, display_name, user_group = auth_result
            return self._create_or_update_user(auth_method, user_id, display_name, user_group)
        return None

    def _create_or_update_user(self, auth_method: str, user_id: str, display_name: str, user_group: str) -> User:
        if auth_method not in self.authenticators.keys():
            raise ValueError(f"Unsupported authentication method: {auth_method}")
        with self.db_connection as db:
            table_name = f"{auth_method}Users"
            cursor = db.execute(f'SELECT user_id, blacklisted, admin, realname, usertype, requests_left FROM "{table_name}" WHERE user_id=?', (user_id,))
            row = cursor.fetchone()

            if row:
                user = User(row[0], bool(row[1]), bool(row[2]), realname=row[3], requests_left=row[5], authmethod=auth_method)
            else:
                db.execute(
                    f'INSERT INTO "{table_name}" (user_id, blacklisted, admin, realname, usertype, requests_left) VALUES (?, ?, ?, ?, ?, ?)',
                    (str(user_id), False, False, str(display_name), str(user_group), int(self.max_requests))
                )
                db.commit()
                user = User(user_id, realname=display_name, usergroup=user_group, authmethod=auth_method)

        return user

    def update_admin_status(self, auth_method: str, ident: str, is_admin: bool):
        if auth_method not in self.authenticators.keys():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            db.execute(f'UPDATE "{table_name}" SET admin=? WHERE user_id=?', (is_admin, ident))
            db.commit()

    def update_banned_status(self, auth_method: str, ident: str, is_banned: bool):
        if auth_method not in self.authenticators.keys():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            db.execute(f'UPDATE "{table_name}" SET blacklisted=? WHERE user_id=?', (is_banned, ident))
            db.commit()

    def refresh_requests(self, inc_by: int = 1):
        with self.db_connection as db:
            for auth_method in self.authenticators.keys():
                table_name = f"{auth_method}Users"
                db.execute(f'''
                    UPDATE "{table_name}"
                    SET requests_left = MIN(?, MAX(0, requests_left + ?))
                ''', (self.max_requests, inc_by))
            db.commit()

    def decrease_requests(self, auth_method: str, user_id: str, dec_by: int = 1):
        for auth_method in self.authenticators.keys():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            db.execute(f'''
                UPDATE "{table_name}"
                SET requests_left = MAX(0, requests_left - ?)
                WHERE user_id = ?
            ''', (dec_by, user_id))
            db.commit()

    def increase_requests(self, auth_method: str, user_id: str, inc_by: int = 1):
        self.decrease_requests(auth_method, user_id, -inc_by)

    def get_requests_remaining(self, auth_method: str, user_id: str) -> Union[int, None]:
        for auth_method in self.authenticators.keys():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            cursor = db.execute(f'SELECT requests_left FROM "{table_name}" WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
