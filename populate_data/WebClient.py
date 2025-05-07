from flask import Flask, render_template, request
import os
import subprocess

print("Current working directory:", os.getcwd())

app = Flask(__name__)
dataset_name = ""
datasets = os.listdir('data_stores')


# Change this to your desired path
UPLOAD_FOLDER = 'source'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_and_submit', methods=['POST'])
def upload_and_submit():
    if 'files' not in request.files:
        return 'No file part', 400
    files = request.files.getlist('files')
    for file in files:
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)  
    # Run the makefile target
    try:
        os.environ['dataset_name']=request.form.get("dataset_name") 
        subprocess.run(['make'], check=True)
        return 'Files uploaded'
    except subprocess.CalledProcessError as e:
        return f'File upload succeeded but Makefile failed: {e}', 500

if __name__ == '__main__':
    app.run(debug=True)
