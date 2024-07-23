"""
User management module for authentication and authorization.

This module provides classes and utilities for managing users,
including authentication methods, database operations, and request tracking.
"""

import secrets
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Tuple, Union
from urllib.parse import urlencode

import requests


class User:
    """
    Provides default implementations for the methods that Flask-Login expects user objects to have.
    """

    # Python 3 implicitly sets __hash__ to None if we override __eq__
    # We set it back to its default implementation
    __hash__ = object.__hash__

    def __init__(self, ident: str, blacklisted=False, admin=False, realname='Student', usergroup='b\'guest\'', authmethod='invalid', requests_left=10, max_requests=10, aka=[]):
        """
        Initialize a User object.

        Args:
            ident (str): The user's identifier.
            blacklisted (bool, optional): Whether the user is blacklisted. Defaults to False.
            admin (bool, optional): Whether the user is an admin. Defaults to False.
            realname (str, optional): The user's real name. Defaults to 'Student'.
            usergroup (str, optional): The user's group. Defaults to 'b\'guest\''.
            authmethod (str, optional): The authentication method. Defaults to 'invalid'.
            requests_left (int, optional): The number of requests left. Defaults to 10.
            max_requests (int, optional): The maximum number of requests. Defaults to 10.
            aka (list, optional): A list of alternate names. Defaults to an empty list.
        """
        self.ident = ident
        self.is_active = not blacklisted
        self.admin = admin
        self.realname = realname
        self.usergroup = usergroup
        self.auth_method = authmethod
        self._requests_remaining = requests_left
        self._max_requests = max_requests
        self.aka: list = aka

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
        """Return the number of requests remaining for the user."""
        return self._requests_remaining

    @requests_remaining.setter
    def requests_remaining(self, num: int):
        """
        Set the number of requests remaining for the user.

        Args:
            num (int): The new number of requests remaining.
        """
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
        return not equal


class LoginStyle:
    
    def __init__(self, icon: str, login_submit: str, direct_submit: bool=False):
        # Not a url, but a controller name for url_for. i.e. 'maeser.github_authorize' or 'localauth'
        self.login_submit = login_submit
        self.direct_submit = direct_submit
        # HTML for a custom form (labels and inputs only)
        self._custom_form: str = '<label for="username" class="form-label">Username</label><input type="text" id="username" name="username" class="form-input" required><label for="password" class="form-label">Password</label><input type="password" id="password" name="password" class="form-input" required>'
        self.icon_html = f'<i class="bi bi-{icon}"></i>'

    @property
    def form_html(self) -> str:
        if self.direct_submit:
            raise ValueError("Cannot use form_html with direct_submit=True")
        return self._custom_form
    
    @form_html.setter
    def form_html(self, html: str):
        self._custom_form = html

class BaseAuthenticator(ABC):
    """
    Base class for authenticators.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Initialize the authenticator with any required arguments.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return the string representation of the authenticator."""
        pass

    @abstractmethod
    def authenticate(self, *args, **kwargs) -> Union[tuple, None]:
        """
        Authenticate a user.

        Args:
            *args: Positional arguments for authentication.
            **kwargs: Keyword arguments for authentication.

        Returns:
            tuple or None: A tuple containing the user's username, real name, and user group if authentication is successful, otherwise None.
        """
        pass

    @abstractmethod
    def fetch_user(self, ident: str) -> Union[User, None]:
        """
        Fetch a user from the authenticator.

        Args:
            ident (str): The identifier of the user to fetch.

        Returns:
            User or None: The fetched user object or None if not found.
        """
        pass
    
    @property
    @abstractmethod
    def style(self) -> LoginStyle:
        """
        Get the login style for the authenticator.

        Returns:
            LoginStyle: The login style object.
        """
        pass


class GithubAuthenticator(BaseAuthenticator):
    """
    Handles authentication with GitHub OAuth.
    """

    def __init__(self, client_id: str, client_secret: str, auth_callback_uri: str, timeout: int = 10):
        """
        Initialize the GitHub authenticator.

        Args:
            client_id (str): The GitHub client ID.
            client_secret (str): The GitHub client secret.
            auth_callback_uri (str): The callback URI for GitHub authentication.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        # Generally this should be set from your Flask app as this will differ between applications
        # url_for('github_auth_callback', _external=True)
        self.auth_callback_uri = auth_callback_uri
        self.timeout = timeout
        self._login_style = LoginStyle('github', 'maeser.github_authorize', direct_submit=True)

    def __str__(self) -> str:
        return 'GitHub'
    
    @property
    def style(self) -> LoginStyle:
        return self._login_style

    def authenticate(self, request_args: dict, oauth_state: str) -> Union[tuple, None]:
        """
        Authenticate a user with GitHub OAuth.

        Args:
            request_args (dict): The request arguments containing the authorization code and state.
            oauth_state (str): The state value used to prevent CSRF attacks.

        Returns:
            tuple or None: A tuple containing the user's username, real name, and user group if authentication is successful, otherwise None.
        """
        if request_args['state'] != oauth_state or 'code' not in request_args:
            print(request_args['state'], oauth_state, 'ERROR') 
            return None

        token_url = 'https://github.com/login/oauth/access_token'
        user_info_url = 'https://api.github.com/user'

        # exchange the authorization code for an access token
        response = requests.post(token_url, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': request_args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': self.auth_callback_uri
        }, headers={'Accept': 'application/json'},
        timeout=self.timeout)

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
        }, timeout=self.timeout)

        if response.status_code != 200:
            print(f'GitHub authentication failed when fetching user info: {response.status_code}', 'ERROR')
            return None

        json_response = response.json()
        print(json_response)
        return json_response['login'], json_response['name'], 'b\'guest\''

    def fetch_user(self, ident: str) -> Union[User, None]:
        """
        Fetch a user from the GitHub API.

        Args:
            ident (str): The username of the user to fetch.

        Returns:
            User or None: The fetched user object or None if the user is not found.
        """
        user_info_url = f'https://api.github.com/users/{ident}'
        response = requests.get(user_info_url)
        if response.status_code == 200:
            json_response = response.json()
            return User(json_response['login'], realname=json_response.get('name', ''), usergroup='b\'guest\'', authmethod='github')
        print(f'WARNING: No GitHub user "{ident}" found')
        return None

    def get_auth_info(self) -> Tuple[str, str]:
        """
        Get the GitHub authorization information.

        Returns:
            tuple: A tuple containing the OAuth state and provider URL.
        """
        authorize_url = 'https://github.com/login/oauth/authorize'
        scopes = ['user:email']

        # generate a random string for the state parameter
        oauth_state = secrets.token_urlsafe(16)

        query_string = urlencode({
            'client_id': self.client_id,
            'redirect_uri': self.auth_callback_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': oauth_state,
        })

        provider_url = authorize_url + '?' + query_string

        return oauth_state, provider_url


class UserManager:
    """
    Manages user operations including authentication, database interactions, and request tracking.
    """

    def __init__(self, db_file_path: str, max_requests: int = 10, rate_limit_interval: int = 180):
        """
        Initialize the UserManager.

        Args:
            db_file_path (str): The file path to the SQLite database.
            max_requests (int, optional): The maximum number of requests a user can have. Defaults to 10.
        """
        self.db_file_path = db_file_path
        self.authenticators: dict[str, BaseAuthenticator] = {}
        self.max_requests = max_requests
        self.rate_limit_interval = rate_limit_interval
        self._create_tables()

    def register_authenticator(self, name: str, authenticator: BaseAuthenticator):
        """
        Register a new authentication method.

        Args:
            name (str): The shorthand name of the authentication method. Must only contain letters.
            authenticator (BaseAuthenticator): The authenticator object.

        Raises:
            ValueError: If the provided name is invalid or the authenticator is already registered.
        """
        if not name.isalpha():
            raise ValueError(f"Invalid authenticator name: {name}, must only contain letters!")
        self.authenticators[name] = authenticator
        with self.db_connection as db:
            self._create_table(db, name)

    @property
    def db_connection(self) -> sqlite3.Connection:
        """
        Open a connection to the SQLite database.

        Returns:
            sqlite3.Connection: The database connection.

        Raises:
            sqlite3.OperationalError: If the database cannot be opened.
        """
        try:
            return sqlite3.connect(self.db_file_path)
        except sqlite3.OperationalError as e:
            print(f'Unable to open sqlite db, using tempory storage: {e}')
            return sqlite3.connect(':memory:')

    def _create_tables(self):
        with self.db_connection as db:
            for auth_method in self.authenticators:
                self._create_table(db, auth_method)

    def _create_table(self, db: sqlite3.Connection, auth_method: str):
        if not auth_method.isalnum():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
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
        """
        Retrieve a user from the database.

        Args:
            auth_method (str): The authentication method used.
            ident (str): The unique identifier of the user.

        Returns:
            User: The user object, or None if not found.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        if not auth_method.isalnum():
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            cursor: sqlite3.Cursor = db.execute(
                f'SELECT user_id, blacklisted, admin, realname, usertype, requests_left FROM "{table_name}" WHERE user_id=?',
                (ident,)
            )
            row = cursor.fetchone()
            if row:
                return User(row[0], bool(row[1]), bool(row[2]), realname=row[3], usergroup=str(row[4]), requests_left=row[5], authmethod=auth_method)
        return None

    def authenticate(self, auth_method: str, *args: Any, **kwargs: Any) -> Union[User, None]:
        """
        Authenticate a user using the specified authentication method.

        Args:
            auth_method (str): The authentication method to use.
            *args: Positional arguments for the authentication method.
            **kwargs: Keyword arguments for the authentication method.

        Returns:
            User: The authenticated user object, or None if authentication fails.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        authenticator = self.authenticators.get(auth_method)
        if not authenticator:
            raise ValueError(f"Unsupported authentication method: {auth_method}")

        auth_result = authenticator.authenticate(*args, **kwargs)
        print(auth_result)
        if auth_result:
            user_id, display_name, user_group = auth_result
            return self._create_or_update_user(auth_method, user_id, display_name, user_group)
        return None

    def _create_or_update_user(self, auth_method: str, user_id: str, display_name: str, user_group: str) -> User:
        """
        Create or update a user in the database.

        Args:
            auth_method (str): The authentication method used.
            user_id (str): The unique identifier of the user.
            display_name (str): The display name of the user.
            user_group (str): The group the user belongs to.

        Returns:
            User: The user object.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        if auth_method not in self.authenticators:
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
        """
        Update the admin status of a user.

        Args:
            auth_method (str): The authentication method used.
            ident (str): The identifier of the user.
            is_admin (bool): Whether the user should be an admin or not.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        if auth_method not in self.authenticators:
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            db.execute(f'UPDATE "{table_name}" SET admin=? WHERE user_id=?', (is_admin, ident))
            db.commit()

    def update_banned_status(self, auth_method: str, ident: str, is_banned: bool):
        """
        Update the banned status of a user.

        Args:
            auth_method (str): The authentication method used.
            ident (str): The identifier of the user.
            is_banned (bool): Whether the user should be banned or not.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        if auth_method not in self.authenticators:
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            db.execute(f'UPDATE "{table_name}" SET blacklisted=? WHERE user_id=?', (is_banned, ident))
            db.commit()

    def refresh_requests(self, inc_by: int = 1):
        """
        Refresh the number of requests for all users by the given amount.

        Args:
            inc_by (int, optional): The amount to increase the requests by. Defaults to 1.
        """
        with self.db_connection as db:
            for auth_method in self.authenticators:
                table_name = f"{auth_method}Users"
                db.execute(f'''
                    UPDATE "{table_name}"
                    SET requests_left = MIN(?, MAX(0, requests_left + ?))
                ''', (self.max_requests, inc_by))
            db.commit()

    def decrease_requests(self, auth_method: str, user_id: str, dec_by: int = 1):
        """
        Decrease the number of requests remaining for a user.

        Args:
            auth_method (str): The authentication method used.
            user_id (str): The identifier of the user.
            dec_by (int, optional): The amount to decrease the requests by. Defaults to 1.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        if auth_method not in self.authenticators:
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
        """
        Increase the number of requests remaining for a user.

        Args:
            auth_method (str): The authentication method used.
            user_id (str): The identifier of the user.
            inc_by (int, optional): The amount to increase the requests by. Defaults to 1.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        if auth_method not in self.authenticators:
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        table_name = f"{auth_method}Users"
        with self.db_connection as db:
            db.execute(f'''
                UPDATE "{table_name}"
                SET requests_left = MIN(?, MAX(0, requests_left + ?))
                WHERE user_id = ?
            ''', (self.max_requests, inc_by, user_id))

    def get_requests_remaining(self, auth_method: str, user_id: str) -> Union[int, None]:
        """
        Get the number of requests remaining for a user.

        Args:
            auth_method (str): The authentication method used.
            user_id (str): The identifier of the user.

        Returns:
            Union[int, None]: The number of requests remaining, or None if the user is not found.

        Raises:
            ValueError: If the provided auth_method is invalid.
        """
        if auth_method not in self.authenticators:
            raise ValueError(f"Invalid authenticator name: {auth_method}")

        user = self.get_user(auth_method, user_id)
        return user.requests_remaining if user else None
