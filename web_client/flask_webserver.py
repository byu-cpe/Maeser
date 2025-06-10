from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash
import os
import subprocess
from werkzeug.utils import secure_filename
import re



app = Flask(__name__)
app.secret_key = 'supersecretkey'  # In production, use a secure and secret value!

# All code below is for the FLASK INTERFACE
# Demo User
USER = {
    'username': 'adam',
    'password': 'ajosiahs',
    'is_admin' : True
}

from flask import request, render_template, redirect, url_for, session
import os

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


def parse_bot_file(bot_txt):
    content = bot_txt
    print(bot_txt)
    # Define regex patterns for sections
    pattern = r'# (\w+)\s+```.*?```\s+((?:.|\n)*?)(?=\n#|\Z)'
    matches = re.findall(pattern, content)

    for section, data in matches:
        lines = [line.strip() for line in data.strip().splitlines() if line.strip()]
        if section == "ModelName" and lines:
            global model_name
            model_name = lines[0]
        elif section == "HostAddress" and lines:
            global host_address
            host_address = lines[0]
        elif section == "Rules":
            global rules
            rules = lines
        elif section == "Contexts":
            global contexts
            contexts = lines


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

UPLOAD_ROOT = '../v2/bot_data'  # base folder to save everything

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

@app.route('/manage_model', methods=['GET', 'POST'])
def find_models():
    print("")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
