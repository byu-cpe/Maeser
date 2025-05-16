from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # In production, use a secure and secret value!

# Dummy user
USER = {
    'username': 'adam',
    'password': 'ajosiahs',
    'is_admin' : True
}

@app.route('/')
def home():
    if 'user' in session:
        return render_template('home.html', username=session['user'], is_admin=USER['is_admin'])
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

@app.route('/admin_portal', methods=['GET','POST'])
def admin_portal():
    if 'user' in session and USER['is_admin']:
        return render_template('admin_portal.html', username=session['user'])
    return redirect(url_for('home'))

UPLOAD_ROOT = 'uploads'  # base folder to save everything

@app.route('/design_model', methods=['GET', 'POST'])
def design_model():
    if 'user' not in session or not USER['is_admin']:
        return redirect(url_for('home'))

    if request.method == 'POST':
        rules = request.form.getlist('rules[]')
        host_address = request.form.get('host_address', '').strip()
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
            bot_file.write("# ModelName\n")
            bot_file.write("```This section holds the user-defined name for the chat bot.```\n")
            bot_file.write(f"{class_code}\n\n")

            bot_file.write("# HostAddress\n")
            bot_file.write("```This should contain the address for the server to forward the flask app to.```\n")
            bot_file.write(f"{host_address}\n\n")

            bot_file.write("# Rules\n")
            bot_file.write("```This section holds the user-defined rules for tailoring the chat bot.```\n")
            for rule in rules:
                bot_file.write(f"{rule}\n")
            bot_file.write("\n")

            bot_file.write("# Contexts\n")
            bot_file.write("```This section holds the user-defined contexts or vetorstores for the bot to use. The bot should be able to think \"what resources do I need for this task?\" and operate accordingly.```\n")
            for context in context_names:
                bot_file.write(f"{context}\n")

        # Run Makefile - pass only CLASS_DIR
        try:
            subprocess.run(
                ['make', f'CLASS_DIR={base_path}'],
                check=True
            )
            flash("Model submitted and Makefile executed successfully!", "success")
        except subprocess.CalledProcessError as e:
            flash(f"Makefile failed: {e}", "error")

        return redirect(url_for('admin_portal'))

    return render_template('design_model.html', username=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
