# Managing Users

This guide details how to manage users in Maeser through built-in Flask routes, and also provides a comprehensive tutorial for implementing your own management system via the `UserManager` API.

---

## Quick Start: Built‑in Flask Routes

Maeser provides ready‑made web interfaces and APIs for user administration. These routes are protected by authentication and admin checks.

### Logs Overview Page
- **Route:** `GET /logs`
- **Description:** Paginated overview of chat logs with filters for branch, user, feedback, and metrics (tokens, cost).
- **Controller:** `chat_logs_overview.controller(chat_session_manager, app_name, favicon)`
- **Example:**  
  ```bash
  curl -u admin:password "https://yourdomain.com/logs?branch=maeser&order=desc"
  ```

### Display Specific Log
- **Route:** `GET /logs/<branch>/<filename>`
- **Description:** Streams a single chat log file for inspection.
- **Controller:** `display_chat_log.controller(chat_session_manager, branch, filename, app_name)`
- **Example:**  
  ```bash
  curl -u admin:password "https://yourdomain.com/logs/maeser/session_20250418.json"
  ```

### User Management Page
- **Route:** `GET /users`
- **Description:** Admin UI for viewing all users, roles, banned status, and quotas.
- **Controller:** `manage_users_view.controller(user_manager, main_logo_login, main_logo_chat, favicon, app_name)`

### User Management API
- **Route:** `POST /users/api`
- **Description:** JSON API for CRUD operations on users: list, grant/revoke admin, ban/unban, adjust quotas, remove users, and clean cache.
- **Controller:** `user_management_api.controller(user_manager)`
- **Sample Payload:**
  ```json
  {
    "type": "toggle-admin",
    "user_auth": "github",
    "user_id": "alice123",
    "new_status": true
  }
  ```
- **Common Commands:**
  | `type`            | Description                           |
  |-------------------|---------------------------------------|
  | `list-users`      | Return all users                      |
  | `toggle-admin`    | Grant or revoke admin role            |
  | `toggle-ban`      | Ban or unban a user                   |
  | `update-requests` | Adjust user quota (`add` / `remove`)  |
  | `remove-user`     | Delete user record                    |
  | `clean-cache`     | Purge non-admin, non-banned users     |
- **Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" \
       -u admin:password \
       -d '{"type":"toggle-ban","user_auth":"github","user_id":"bob456","new_status":true}' \
       https://yourdomain.com/users/api
  ```

---

## Implementing Your Own User Management

If you prefer to build a custom management interface or scripts, use the `UserManager` API directly. The sections below guide you through authentication setup, user operations, quota management, and automation.

### Prerequisites

- Maeser installed and configured (`pip install -e .` or `make setup`).
- A `config.yaml` with `USERS_DB_PATH` pointing to your SQLite database.
- Registered authenticators in your app or REPL.

```python
from maeser.user_manager import UserManager, GithubAuthenticator, LDAPAuthenticator

# Initialize UserManager\ nuser_manager = UserManager(
    db_file_path="path/to/users.db",
    max_requests=100,
    rate_limit_interval=60
)

# Register authenticators
github_auth = GithubAuthenticator(...)  
ldap_auth = LDAPAuthenticator(...)
user_manager.register_authenticator("github", github_auth)
user_manager.register_authenticator("ldap", ldap_auth)
```

### 1. Listing Users

```python
all_users = user_manager.list_users()
github_users = user_manager.list_users(auth_filter="github")
admin_users = user_manager.list_users(admin_filter="admin")
banned_users = user_manager.list_users(banned_filter="banned")
```

### 2. Admin Privileges

```python
# Grant admin\ nuser_manager.update_admin_status("github", "alice123", True)
# Revoke admin
user_manager.update_admin_status("github", "bob456", False)
```

### 3. Banning & Unbanning

```python
user_manager.update_banned_status("github", "malicious_user", True)
user_manager.update_banned_status("github", "good_user", False)
```

### 4. Quota Management

```python
remaining = user_manager.get_requests_remaining("github", "alice123")
user_manager.refresh_requests()
user_manager.decrease_requests("github", "alice123")
user_manager.increase_requests("github", "alice123", inc_by=5)
```

### 5. Initializing the First Admin

```python
user = user_manager.authenticate("github", code="<oauth-code>")
user_manager.update_admin_status("github", user.user_id, True)
```

Or update the DB directly:
```sql
UPDATE githubUsers SET admin=1 WHERE user_id='alice123';
```

### 6. Removing Users

```python
user_manager.remove_user_from_cache("github", "temp_user", force_remove=True)
```

### 7. Cleanup & Maintenance

```python
removed = user_manager.clean_cache()
to_remove = user_manager.list_cleanables()
```

### 8. Automating with Scripts

Create CLI scripts (e.g., `scripts/add_admin.py`) using `UserManager` methods to streamline admin tasks.

---

With both built‑in routes and the flexible API, you can manage Maeser users in whichever manner best fits your infrastructure and workflows.

