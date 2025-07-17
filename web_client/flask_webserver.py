from flask import Flask, render_template, request, redirect, url_for, session
from config import UPLOAD_ROOT
import os
import subprocess
from werkzeug.utils import secure_filename
import shutil
from design_model import (
    get_model_config, save_model,
    delete_datasets, remove_class_model,
    load_rules, load_datasets
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # In production, use a secure and secret value!

# All code below is for the FLASK INTERFACE
# Demo User
USER = {
    'username': 'adam',
    'password': 'ajosiahs',
    'is_admin' : True
}

# Global Variables
model_name = ""
host_address = ""
rules = []
contexts = []

# decorator for login checking
import functools
def require_login(func):
    @functools.wraps(func) # updates metadata so that check_login.__name__ == func.__name__
    def check_login(*args, **kwargs):
        if 'user' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return check_login

@app.route('/')
@require_login
def home():
    return render_template('admin_portal.html', username=session['user'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USER['username'] and password == USER['password']:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/design_model', methods=['GET', 'POST'])
@require_login
def design_model():
    if request.method == 'POST':
        # Get model config
        try:
            model_config:tuple = get_model_config(UPLOAD_ROOT)
        except AttributeError as e:
            print(f"Unable to use model config: {e}")
            return redirect(url_for('design_model'))
        
        # Save model
        try:
            save_model(UPLOAD_ROOT, *model_config)
        except subprocess.CalledProcessError as e:
            print(f"Makefile failed: {e}")
            return redirect(url_for('design_model'))
        finally:
            print("Model submitted and Makefile executed successfully!")
            return redirect(url_for('manage_models'))

    return render_template('design_model.html', username=session['user'])

@app.route('/manage_models', methods=['GET', 'POST'])
@require_login
def manage_models():
    if request.method == 'POST':
        class_code = request.form.get("class_code")
        if not class_code:
            print("Error: Class Code is required.")
            return redirect(url_for('design_model'))
        else:
            remove_class_model(UPLOAD_ROOT, class_code)
        return redirect(url_for('manage_models'))

    # List all class_code folders inside UPLOAD_ROOT
    models = []
    for item in os.listdir(UPLOAD_ROOT):
        model_path = os.path.join(UPLOAD_ROOT, item)
        if os.path.isdir(model_path):
            models.append(item)  # item is the class_code

    return render_template('manage_models.html', username=session['user'], models=models)


@app.route('/edit_model/<class_code>', methods=['GET', 'POST'])
@require_login
def edit_model(class_code):
    # Get important file paths
    model_dir = os.path.join(UPLOAD_ROOT, secure_filename(class_code))
    bot_path = os.path.join(model_dir, 'bot.txt')

    if request.method == 'POST':
        # Get model config
        try:
            model_config:tuple = get_model_config(UPLOAD_ROOT)
        except AttributeError as e:
            print(f"Unable to use model config: {e}")
            return redirect(url_for('edit_model', class_code=class_code))
        
        # Delete selected datasets
        delete_datasets(model_dir)

        # Save model
        try:
            save_model(UPLOAD_ROOT, *model_config)
        except subprocess.CalledProcessError as e:
            print(f"Makefile failed: {e}")
            return redirect(url_for(f'/edit_model/{class_code}'))
        finally:
            print("Model submitted and Makefile executed successfully!")
            return redirect(url_for('manage_models'))

    # Get rules and datasets
    rules = load_rules(bot_path)
    current_datasets = load_datasets(model_dir)

    return render_template(
        'edit_model.html',
        class_code=class_code,
        rules=rules,
        current_datasets=current_datasets,
        username=session['user'],
    )

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
