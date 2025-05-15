from flask import Flask, render_template, request, redirect, url_for, session

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

@app.route('/design_model', methods=['GET','POST'])
def design_model():
    if 'user' in session and USER['is_admin']:
        return render_template('design_model.html', username=session['user'])
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
