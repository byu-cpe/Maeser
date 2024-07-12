from flask import render_template, redirect, url_for, request, session
from flask_login import login_user
from urllib.parse import urljoin, urlparse

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def login_controller(auth_manager):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = auth_manager.authenticate_caedm(username, password)
        if user is None:
            return render_template('login.html', message='CAEDM Authentication Failed')
        if not user.is_active:
            return render_template('login.html', message=f'User {user.full_id_name} is Banned')
        
        login_user(user)
        
        next_url = request.args.get('next')
        if not next_url or not is_safe_url(next_url):
            next_url = url_for('main_page')

        return redirect(next_url)

    next_url = request.args.get('next')
    message = request.args.get('message', '')

    return render_template('login.html', message=message, next=next_url)

def github_authorize_controller(current_user, github_authenticator):
    if not current_user.is_anonymous:
        return redirect(url_for('main_page'))
    
    session['oauth2_state'] , provider_url = github_authenticator.get_auth_info()

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_url)

def github_auth_callback_controller(current_user, auth_manager):
    if not current_user.is_anonymous:
        return redirect(url_for('main_page'))

    # if there was an error before auth, render the login page with the error message
    if 'error' in request.args:
        print(f'An error occurred during the auth callback before authentication: {request.args}')
        error_message = request.args.get('error_description', 'Authentication failed')
        return render_template('login.html', message=error_message)
    
    oauth_state = session.get('oauth2_state')

    user = auth_manager.authenticate_github(request.args, oauth_state)
    if user is None:
        return render_template('login.html', message='GitHub Authentication Failed')
    if not user.is_active:
        return render_template('login.html', message=f'User {user.full_id_name} is Banned')
    
    login_user(user)

    return redirect(url_for('main_page'))