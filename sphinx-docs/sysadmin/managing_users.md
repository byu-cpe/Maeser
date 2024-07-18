# Managing users

Use the `mum` (Maeser User Manager) script to manage users without having to manually poke the SQLite database.

## Why Is This Needed?

This is needed for managing user permissions more easily, including import things such as admin access.
While you *can* manually edit the SQLite database (that's all this script really does), it makes it simpler
because it transparently handles all users of all authentication types, including ones that have never logged in,
and makes sure that they actually exist (as in, it verifies the net ids).
In the future, this script should support users who authenticate using other methods (such as through GitHub).

TODO