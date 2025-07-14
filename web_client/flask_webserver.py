from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash
from config import UPLOAD_ROOT
import os
import subprocess
from werkzeug.utils import secure_filename
import shutil

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

@app.route('/')
def home():
    if 'user' in session:
        return render_template('admin_portal.html', username=session['user'])
    return redirect(url_for('login'))

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
def design_model():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        rules = request.form.getlist('rules[]')
        class_code = request.form.get('class_code', '').strip()

        if not class_code:
            flash("Class Code is required.", "error")
            return redirect(url_for('design_model'))

        base_path = os.path.join(UPLOAD_ROOT, secure_filename(class_code))
        os.makedirs(base_path, exist_ok=True)

        file_groups = []  # Initialize list of saved group directories

        # Save uploaded files grouped properly
        for key in request.files:
            if key.startswith('file_groups'):
                idx = key.split('[')[1].split(']')[0]
                group_name = request.form.get(f'file_groups[{idx}][name]', f'Group_{idx}')
                group_dir = os.path.join(base_path, secure_filename(group_name))
                os.makedirs(group_dir, exist_ok=True)

                files = request.files.getlist(f'file_groups[{idx}][files]')
                for f in files:
                    if f and f.filename.endswith('.pdf'):
                        filename = secure_filename(f.filename)
                        f.save(os.path.join(group_dir, filename))

                file_groups.append(group_dir)  # Append each group directory

        context_names = [os.path.basename(path) for path in file_groups]

        # Write bot.txt with all required sections
        bot_file_path = os.path.join(base_path, 'bot.txt')
        with open(bot_file_path, 'w', encoding='utf-8') as bot_file:
            bot_file.write("#NAME\n")
            bot_file.write(f"{class_code}\n")

            bot_file.write("#RULES\n")
            for rule in rules:
                bot_file.write(f"{rule}\n")


            bot_file.write("#DATASETS\n")
            for context in context_names:
                bot_file.write(f"{context.lower()}\n")

        # Run Makefile - pass only CLASS_DIR
        try:
            subprocess.run(
                ['make', f'CLASS_DIR={base_path}'],
                check=True
            )
            flash("Model submitted and Makefile executed successfully!", "success")
        except subprocess.CalledProcessError as e:
            flash(f"Makefile failed: {e}", "error")

        return redirect(url_for('home'))

    return render_template('design_model.html', username=session['user'])

@app.route('/manage_models', methods=['GET'])
def manage_models():
    if 'user' not in session:
        return redirect(url_for('login'))

    # List all class_code folders inside UPLOAD_ROOT
    models = []
    for item in os.listdir(UPLOAD_ROOT):
        model_path = os.path.join(UPLOAD_ROOT, item)
        if os.path.isdir(model_path):
            models.append(item)  # item is the class_code

    return render_template('manage_models.html', username=session['user'], models=models)


@app.route('/edit_model/<class_code>', methods=['GET', 'POST'])
def edit_model(class_code):
    if 'user' not in session:
        return redirect(url_for('login'))

    model_dir = os.path.join(UPLOAD_ROOT, secure_filename(class_code))
    bot_path = os.path.join(model_dir, 'bot.txt')

    if request.method == 'POST':
        # Handle rules update
        new_rules = request.form.getlist('rules[]')

        # Handle file uploads
        file_groups = []
        for key in request.files:
            if key.startswith('file_groups'):
                idx = key.split('[')[1].split(']')[0]
                group_name = request.form.get(f'file_groups[{idx}][name]', f'Group_{idx}')
                group_dir = os.path.join(model_dir, secure_filename(group_name))
                os.makedirs(group_dir, exist_ok=True)

                files = request.files.getlist(f'file_groups[{idx}][files]')
                for f in files:
                    if f and f.filename.endswith('.pdf'):
                        f.save(os.path.join(group_dir, secure_filename(f.filename)))

                file_groups.append(group_dir)

        # Handle dataset deletion
        to_delete = request.form.getlist('delete_datasets[]')
        for group in to_delete:
            group_path = os.path.join(model_dir, secure_filename(group))
            if os.path.exists(group_path) and os.path.isdir(group_path):
                shutil.rmtree(group_path)

        # Rewrite bot.txt
        with open(bot_path, 'w', encoding='utf-8') as bot_file:
            bot_file.write("#NAME\n")
            bot_file.write(f"{class_code}\n")

            bot_file.write("#RULES\n")
            for rule in new_rules:
                bot_file.write(f"{rule}\n")

            bot_file.write("#DATASETS\n")
            for group in os.listdir(model_dir):
                group_path = os.path.join(model_dir, group)
                if os.path.isdir(group_path):
                    bot_file.write(f"{group.lower()}\n")

        # Re-vectorize via make
        try:
            subprocess.run(['make', f'CLASS_DIR={model_dir}'], check=True)
            flash("Model updated and Makefile executed!", "success")
        except subprocess.CalledProcessError as e:
            flash(f"Makefile failed: {e}", "error")

        return redirect(url_for('manage_models'))

    # Load rules from bot.txt
    rules = []
    if os.path.exists(bot_path):
        with open(bot_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            collecting = False
            for line in lines:
                if line.strip() == "#RULES":
                    collecting = True
                    continue
                if line.strip().startswith("#") and collecting:
                    break
                if collecting:
                    rules.append(line.strip())

    # Load current datasets
    current_datasets = [
        d for d in os.listdir(model_dir)
        if os.path.isdir(os.path.join(model_dir, d)) and d != '__pycache__'
    ]

    return render_template('edit_model.html',
                           class_code=class_code,
                           rules=rules,
                           current_datasets=current_datasets,
                           username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
