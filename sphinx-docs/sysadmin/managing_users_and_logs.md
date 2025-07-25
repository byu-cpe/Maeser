# Managing Users and Chat Logs

The Maeser Flask app comes with a built-in web interface for [**User Management**](#user-management-page) and [**Chat Logs Management**](#chat-logs-management-page). These interfaces make it easy for an administrator to monitor usage of their chatbot and modify user permissions.

---

## Prerequisites
- **Administrator Privileges**: You must be an administrator to access the User Management and Chat Logs Management pages. For instructions on how to acquire administrator privileges, see [**Obtaining Administrator Privileges**](#obtaining-administrator-privileges).

## User Management Page

The User Management page lets you see and modify the permissions of all users registered in your Maeser app.

### Filters

The User Management page provides the following filters to sort through your user database:
1. **Authenticators:** Display users from a specific authentication method. (**Note:** This filter is only visible if you have more than one authenticator registered with your app.) 
2. **Admin Status:** Display either users that have administrator privileges or users that do not.
3. **Banned Status:** Display either banned or non-banned users.

### Edit User Options

To edit the permissions and options of a user, click on their user card in the list of users. A menu will appear where you can change the following:
- **Admin Status:** Whether the user has elevated or standard privileges.
- **Ban Status:** Whether or not the user is banned from accessing your web interface.
- **Requests:** The number of messages the user has left before they will be rate-limited.
- **Remove User:** Deletes a user from the user database. The user will have to re-create their account the next time they log in.

### Return Home

To return home, simply click your Maeser app's logo at the top-left corner of the page.

---

## Chat Logs Management Page

The Chat Logs Management page lets you see the conversation history between users and your chatbot. Each log file corresponds to one conversation created by a user.

### Filters

The Chat Logs Management page has the following sorting and filtering options:

- **Sort by Modification or Creation Time:** Whether the logs should be sorted by when they were modified or when they were created.
- **Order:** The direction in which the log entries should be sorted.
- **User:** Display log files from a specific user.
- **Feedback:** Display either log files with user-submitted feedback or log files without feedback.

### List of Log Files

The list of log files on the Chat Logs Management page displays a high-level overview of each log, including:
- **User:** Formatted like `authenticator.user_id`.
- **Log File Name:** A string of numbers followed by `-authenticator-user_id.log`.
- **Creation Date/Time:** The time and date the log file was created, or in other words, the time and date the conversation started.
- **Last Modified Date/Time:** The time and date the log file was last modified, or in other words, the time and date of the last message in the conversation.
- **Feedback:** True or False, depending on whether the user submitted feedback in that conversation thread.

A few helpful aggregate statistics are listed above the list of log files:
- **Total Tokens**
- **Total Cost**

These statistics are a grand total for your Maeser app, summed from all log files saved.

### View Individual Logs

To view the contents of a single log file, simply click its file name to open its contents in a new page.

The top of the log file contains statistics for the entire conversation thread:
- **Name:** The name of the user conversing with your chatbot.
- **User Authentication:** The authenticator and user id of the user, formatted like `authenticator.user_id`
- **Time:** The time and date the log file was created, or in other words, the time and date the conversation started.
- **Branch:** The chat branch selected for the conversation. This should correspond to one of the branches registered to your app's `ChatSessionManager` object (in your app's Flask script).
- **Total Cost:** The total cost of the conversation thread, accrued from the total tokens used during response generation.
- **Total Tokens:** The total number of tokens used in the conversation thread by the LLM for response generation.

The rest of the log file consists of the conversation history, following this general form:
```
────────────────────
<user question>
────────────────────
<chatbot response>
<response statistics>
────────────────────
```

The response statistics are as follows:
- **Cost:** The precise cost of processing the chatbot's response.
- **Tokens:** The number of tokens used to process the chatbot's response.
- **Time to Response:** The amount of time it took for the chatbot to generate a response.
- **Feedback:** Either "Positive" or "Negative" depending on the feedback selected by the user. (**Note:** This statistic is only visible if the user left feedback on the chatbot's response.)

> **Note: Vectorstore Context in Log File**
>
> The chat log files also record the context pulled from the vectorstore(s) that was used by the chatbot to generate a relevant response. For brevity, this context is not exposed on the Chat Logs Management web view, but it can be accessed directly in your chat logs directory if desired.

The bottom of the Log page contains the link "Back to list", which will take you back to the **List of Log Files**.

### Return Home

To return home, simply click your Maeser app's logo at the top-left corner of the page. If you are viewing a single log file, first click "Back to list"; then click your Maeser app's logo at the top-left corner of the page.

---

## Obtaining Administrator Privileges

Before you can access the User and Chat Logs Management pages, you must first have administrator privileges. You have three options to acquire these privileges:

1. [**Receive privileges from another administrator.**](#receive-privileges-from-another-administrator)
2. [**Use `user_manager.update_admin_status()`.**](#use-user_managerupdate_admin_status)
3. [**Modify the user database directly.**](#modify-the-user-database-directly)

For these methods to work, you must have logged in to your Maeser app at least once. You can **check your administrator status** by opening the side panel via the button at the top-left corner of the page. If you see buttons labeled "User Management" and "Logs", then you have administrator privileges; if these buttons are missing, then you do not have administrator privileges.

### Receive Privileges From Another Administrator

If another user already has administrator rights, they can simply log in and remotely grant administrator privileges to your account via the [**User Management Page**](#user-management-page). This is the most straightforward approach, but the other methods listed will work if you are unable to receive privileges from another administrator.

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

Save these changes and restart your Maeser app; you should now have administrator privileges. You may now remove `user_manager.update_admin_status(...)` from your code and your privileges will still be elevated.

### Modify the User Database Directly

The SQLite database file used to store user data is located at the path specified by `accounts_db_path` in your app's `config.yaml` (located at `chat_logs/users.db` by default). You will need a program that can open SQLite database files; several programs and code editor extensions exist that can do this. To grant yourself administrator privileges using this method, do the following:
1. **Open the database file** with a program of your choice.
2. **Find your row in the database** by entering the table corresponding to your authentication method (e.g. `githubUsers` for GitHub) and using the `user_id` and `realname` columns to locate your entry.
3. **Toggle your admin status** by changing the value of the "admin" cell on your row from 0 to 1.

Once you commit this change to the database, you will be granted administrator privileges.