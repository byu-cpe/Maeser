# Managing Users and Chat Logs

The Maeser Flask app comes with a built-in web interface for [**User Management**](#user-management-page) and [**Chat Logs Management**](#chat-logs-management-page). These interfaces make it easy for an administrator to monitor usage of their chatbot and modify user permissions.

---

## Prerequisites
- **Administrator Privileges**: You must be an admin to access the User Management and Chat Logs Management pages. For instructions on how to acquire administrator privileges, see [**Obtaining Administrator Privileges**](#obtaining-administrator-privileges).

## User Management Page

The User Management page lets you see and modify the permissions of all users registered in your Maeser app.

### Filters

The User Management page provides the following filters to sort through your user database:
1. **Authenticators:** Display users from a specific authentication method. (**Note:** This filter is only visible if you have more than one authenticator registered with your app.) 
2. **Admin Status:** Display either users that have administrator priviliges or users that do not.
3. **Banned Status:** Display either banned or non-banned users.

### Edit User Options

To edit the permissions and options of a user, click on their user card in the list of users. A menu will appear where you can change the following:
- **Admin Status:** Whether the user has elevated or standard privileges.
- **Ban Status:** Whether or not the user is banned from accessing your web server.
- **Requests:** The number of messages the user has left before they will be rate-limited.
- **Remove User:** Deletes a user from the user database. The user will have to re-create their account the next time they log in.

### Return Home

To return home, simply click your Maeser app's logo at the top-left corner of the page.

---

## Chat Logs Management Page

...

---

## Obtaining Administrator Privileges

Before you can access the User and Chat Logs Management pages, you must first have administrator privileges. You have three options to acquire these priveleges:

1. [**Receive privileges from another administrator.**](#receive-privileges-from-another-administrator)
3. [**Use `user_manager.update_admin_status()`.**](#use-user_managerupdate_admin_status)
2. [**Modify the user database directly.**](#modify-the-user-database-directly)

For these methods to work, you must have logged in to your Maeser app at least once. You can **check your admin** status by opening the side panel via the button at the top-left corner of the page. If you see buttons labeled "User Management" and "Logs", then you have administrator privileges; if these buttons are missing, then you do not have administrator privileges.

### Receive Privileges From Another Administrator

If another user already has administrator rights, they can simply login and remotely grant administrator privileges to your account via the [**User Management Page**](#user-management-page). This is the most straightforward approach, but the other methods listed will work if you are unable to receive privileges from another administrator.

### Use `user_manager.update_admin_status()`

This method will require you to temporarily modify your Maeser app's Flask script. Open your Flask script and locate where your user manager is registered with its authenticators. This section will look similar to the following:

```python

user_manager = UserManager(db_file_path=USERS_DB_PATH, max_requests=MAX_REQUESTS, rate_limit_interval=RATE_LIMIT_INTERVAL)
user_manager.register_authenticator(name="github", authenticator=github_authenticator)

```

Below this section, add the following code:

```python

user_manager = UserManager(db_file_path=USERS_DB_PATH, max_requests=MAX_REQUESTS, rate_limit_interval=RATE_LIMIT_INTERVAL)
user_manager.register_authenticator(name="github", authenticator=github_authenticator)

# --- New code starts here --- #
user_manager.update_admin_status(
    auth_method="github",
    ident="your_username",
    is_admin=True,
)

```

Replace `your_username` with the username registered under your authenticator, and if using an authenticator other than GitHub, replace `github` with the name of your authenticator.

Save these changes and restart your Maeser app; you should now have administrator privileges. You may now remove `user_manager.update_admin_status(...)` from your code and your priviliges will still be elevated.

### Modify the User Database Directly

The database file used to store user data is located at the path specified by `accounts_db_path` in your app's `config.yaml` (located at `chat_logs/users.db` by default). This file is an SQLite database; several programs and code editor extensions exist that can open and modify SQLite files, so pick the program of your choice to do so. To grant yourself administrator privileges using this method, open the database file, enter the table corresponding to your authentication method (e.g. `githubUsers` for GitHub), and find your row entry in the table (with help from the `user_id` and `realname` columns). Look for the column labeled `admin` and change the value at this column and on your row from 0 to 1. Once you commit this change to the database, you will be granted administrator privileges.