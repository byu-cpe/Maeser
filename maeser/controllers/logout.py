from flask_login import logout_user
from flask import redirect, url_for, session

def controller():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    return redirect(url_for('login'))