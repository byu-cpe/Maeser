# SPDX-License-Identifier: LGPL-3.0-or-later

from flask import Flask, render_template, request, redirect, url_for, session
from maeser.config import VEC_STORE_PATH as UPLOAD_ROOT, OPENAI_API_KEY
import os
import functools
from werkzeug.utils import secure_filename
from design_model import (
    get_model_config, save_model,
    delete_datasets, remove_class_model,
    load_rules, load_datasets
)

if UPLOAD_ROOT == "" or UPLOAD_ROOT == "...":
    print(f'\033[0;31mERROR: vec_store_path ("{UPLOAD_ROOT}") cannot be unassigned.')
    exit(1)
if OPENAI_API_KEY == "" or OPENAI_API_KEY == "...":
    print(f'\033[0;31mERROR: openai_api_key ("{OPENAI_API_KEY}") cannot be unassigned.')
    exit(1)

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
        except Exception as e:
            print(f"Unable to generate model: {e}")
            return redirect(url_for('design_model'))
        finally:
            print("Model generation complete. Please check the terminal output to ensure no errors were thrown.")
            return redirect(url_for('manage_models'))

    return render_template('design_model.html', username=session['user'])

@app.route('/manage_models', methods=['GET', 'POST'])
@require_login
def manage_models():
    if request.method == 'POST':
        course_id = request.form.get("course_id")
        if not course_id:
            print("Error: Course ID is required.")
            return redirect(url_for('design_model'))
        else:
            remove_class_model(UPLOAD_ROOT, course_id)
        return redirect(url_for('manage_models'))

    # List all course_id folders inside UPLOAD_ROOT
    models = []
    for item in os.listdir(UPLOAD_ROOT):
        model_path = os.path.join(UPLOAD_ROOT, item)
        if os.path.isdir(model_path):
            models.append(item)  # item is the course_id

    return render_template('manage_models.html', username=session['user'], models=models)


@app.route('/edit_model/<course_id>', methods=['GET', 'POST'])
@require_login
def edit_model(course_id):
    # Get important file paths
    model_dir = os.path.join(UPLOAD_ROOT, secure_filename(course_id))
    bot_path = os.path.join(model_dir, 'bot.txt')

    if request.method == 'POST':
        # Get model config
        try:
            model_config:tuple = get_model_config(UPLOAD_ROOT)
        except AttributeError as e:
            print(f"Unable to use model config: {e}")
            return redirect(url_for('edit_model', course_id=course_id))
        
        # Delete selected datasets
        delete_datasets(model_dir)

        # Save model
        try:
            save_model(UPLOAD_ROOT, *model_config)
        except Exception as e:
            print(f"Unable to generate model: {e}")
            return redirect(url_for(f'/edit_model/{course_id}'))
        finally:
            print("Model generation complete. Please check the terminal output to ensure no errors were thrown.")
            return redirect(url_for('manage_models'))

    # Get rules and datasets
    rules = load_rules(bot_path)
    current_datasets = load_datasets(model_dir)

    return render_template(
        'edit_model.html',
        course_id=course_id,
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
