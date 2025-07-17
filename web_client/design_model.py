"""
This is a helper script used by flask_webserver.py
that handles designing and editing class models
"""

from flask import request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
import subprocess
import shutil

# Retrieve model config from request
def get_model_config(upload_root:str) -> tuple[
    str, str, str, list[str], dict[str, list[FileStorage]]
]:
    # Make sure class_code is defined
    class_code = request.form.get('class_code', '').strip()
    if not class_code:
        raise AttributeError("No class code found in request form.")
    
    # Get important file paths
    model_dir = os.path.join(upload_root, secure_filename(class_code))
    os.makedirs(model_dir, exist_ok=True) # TODO: remove this?
    bot_path = os.path.join(model_dir, 'bot.txt')

    # Get ruleset
    rules = request.form.getlist('rules[]')

    # Get datasets
    datasets = {}
    for key in request.files:
        if key.startswith('file_groups'):
            # Get dataset path
            idx = key.split('[')[1].split(']')[0]
            dataset_name = request.form.get(f'file_groups[{idx}][name]', f'Group_{idx}').lower()
            dataset_path = os.path.join(model_dir, secure_filename(dataset_name))
            # os.makedirs(dataset_path, exist_ok=True)

            # Get files to go inside dataset
            files = request.files.getlist(f'file_groups[{idx}][files]')
            datasets[dataset_path] = files

            # # Save files
            # for f in files:
            #     if f and f.filename.endswith('.pdf'):
            #         filename = secure_filename(f.filename)
            #         f.save(os.path.join(dataset_path, filename))
    return class_code, model_dir, bot_path, rules, datasets

# Save model given config
def save_model(
    upload_root:str, class_code: str, model_dir: str, bot_path:str, rules: list[str], datasets: dict[str, list[FileStorage]]
):
    # Make model dir
    os.makedirs(model_dir, exist_ok=True)

    # Save datasets
    for dataset_path, files in datasets.items():
        os.makedirs(dataset_path, exist_ok=True)
        for f in files:
            if f and f.filename.endswith('.pdf'):
                filename = secure_filename(f.filename)
                f.save(os.path.join(dataset_path, filename))

    # Write bot.txt with all required sections
    with open(bot_path, 'w', encoding='utf-8') as bot_file:
        bot_file.write("#NAME\n")
        bot_file.write(f"{class_code}\n")

        bot_file.write("#RULES\n")
        for rule in rules:
            bot_file.write(f"{rule}\n")

        bot_file.write("#DATASETS\n")
        for dataset in os.listdir(model_dir):
            dataset_dir = os.path.join(model_dir, dataset)
            if os.path.isdir(dataset_dir):
                bot_file.write(f"{dataset.lower()}\n")

    # Process datasets
    process_datasets(model_dir)

# Process datasets via Makefile
def process_datasets(model_dir:str):
    subprocess.run(
        ['make', f'CLASS_DIR={model_dir}'],
        check=True,
    )

# Delete datasets
def delete_datasets(model_dir:str):
    to_delete = request.form.getlist('delete_datasets[]')
    for dataset in to_delete:
        group_path = os.path.join(model_dir, secure_filename(dataset))
        if os.path.exists(group_path) and os.path.isdir(group_path):
            shutil.rmtree(group_path)
