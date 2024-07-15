import secrets
import sqlite3
from typing import Tuple, Union, Dict, Any
from urllib.parse import urlencode
import requests
from abc import ABC, abstractmethod

class User:
    """
    This provides default implementations for the methods that Flask-Login expects user objects to have.
    """

    # Python 3 implicitly sets __hash__ to None if we override __eq__
    # We set it back to its default implementation
    __hash__ = object.__hash__

    def __init__(self, ident: str, blacklisted=False, admin=False, realname='Student', usergroup='b\'guest\'', authmethod='caedm', requests_left=10, max_requests=10, aka=list()):
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

class BaseAuthenticator(ABC):
    """
    Base class for authenticators.
    """

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initialize the authenticator with any required arguments.
        """
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        return 'BaseAuthenticator'
    
    @abstractmethod
    def authenticate(self, *args: Any, **kwargs: Any) -> Union[tuple, None]:
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

class GithubAuthenticator(BaseAuthenticator):
    """
    This class handles authentication with GitHub OAuth.
    """

    def __init__(self, client_id: str, client_secret: str, auth_callback_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        # Generally this should be set from your Flask app as this will differ between applications
        # url_for('github_auth_callback', _external=True)
        self.auth_callback_uri = auth_callback_uri
        
    def __str__(self) -> str:
        return 'GithubAuthenticator'

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

    def fetch_user(self, ident: str) -> Union[User, None]:
        """
        Fetch a user from the GitHub API.

        Args:
            username (str): The username of the user to fetch.

        Returns:
            User or None: The fetched user object or None if the user is not found.
        """
        user_info_url = f'https://api.github.com/users/{ident}'
        response = requests.get(user_info_url)
        if response.status_code == 200:
            json_response = response.json()
            return User(json_response['login'], realname=json_response.get('name', ''), usergroup='b\'guest\'', authmethod='github')
        print(f'No GitHub user "{ident}" found', "WARNING")
        return None
    
    def get_auth_info(self) -> Tuple[str, str]:
        authorize_url = 'https://github.com/login/oauth/authorize'
        scopes = ['user:email']

        # generate a random string for the state parameter
        oauth_state = secrets.token_urlsafe(16)
        
        # create a query string with all the OAuth2 parameters
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

    def __init__(self, db_file_path: str, max_requests: int = 10):
        self.db_file_path = db_file_path
        self.authenticators: Dict[str, BaseAuthenticator] = {}
        self.max_requests = max_requests
        self._create_tables()

    def register_authenticator(self, name: str, authenticator: BaseAuthenticator):
        """
        Register a new authentication method.

        Args:
            name (str): The name of the authentication method.
            authenticator (BaseAuthenticator): The authenticator object.

        Raises:
            ValueError: If the provided name is invalid or the authenticator is already registered.
        """
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
