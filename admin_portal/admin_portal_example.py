from maeser.admin_portal import run_admin_portal

# Set a username and password
USERNAME = "karl"
PASSWORD = "karlgmaeser1"

# Use a secure key in production. You can generate a secret key in the terminal using python's
# `secrets` module:
# `$ python -c 'import secrets; print(secrets.token_hex())'`
SECRET_KEY: str = "super-secret-key"

run_admin_portal(
    username=USERNAME,
    password=PASSWORD,
    secret_key=SECRET_KEY,
)