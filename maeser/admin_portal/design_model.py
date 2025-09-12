# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module is used by flask_admin_portal.py and contains several helper functions that handle designing and editing class chatbot models.
"""

from flask import request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
import shutil
from maeser.admin_portal.extract_figures import extract_all_figures
from maeser.admin_portal.extract_text import extract_all_pdf_texts
from maeser.admin_portal.vector_store_operator import vectorize_data

def get_model_config(upload_root: str) -> tuple[
    str, str, str, list[str], dict[str, list[FileStorage]]
]:
    """Retrieves config for a course model from a post request.

    Args:
        upload_root (str): The root directory where all course models are created and modified.

    Raises:
        AttributeError: If the request form is missing 'course_id'.

    Returns:
        ( course_id: str, model_dir: str, bot_path: str, rules: list[str], datasets: dict[str, list[FileStorage]] ): Parsed config data from the request form.
        See the parameters of `save_model` for more info.
    """
    # Make sure course_id is defined
    course_id = request.form.get('course_id', '').strip()
    if not course_id:
        raise AttributeError("No course ID found in request form.")
    
    # Get important file paths
    model_dir = os.path.join(upload_root, secure_filename(course_id))
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
    return course_id, model_dir, bot_path, rules, datasets

def save_model(
    upload_root: str, course_id: str, model_dir: str, bot_path: str, rules: list[str], datasets: dict[str, list[FileStorage]]
):
    """Saves the course model using the provided config.

    Args:
        upload_root (str): The root directory where all course models are created and modified.
        course_id (str): The code used to identify the class.
        model_dir (str): The directory to where the model's data will be saved.
        bot_path (str): The path to where the model's 'bot.txt' file will be saved.
        rules (list[str]): The list of rules for the model's chatbot to follow.
        datasets (dict[str, list[FileStorage]]): A dictionary containing the path to each dataset (key) and a list of its files (value).
    """
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
        bot_file.write(f"{course_id}\n")

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

def process_datasets(model_dir: str):
    print(f"Processing subdirectories in {model_dir}...")
    dirs = sorted([
        os.path.join(model_dir, dir) for dir in os.listdir(model_dir)
        if os.path.isdir(os.path.join(model_dir, dir))
        ])
    for dir in dirs:
        if os.path.exists(os.path.join(dir, "index.faiss")):
            print(f"(dataset for {dir} already exists, skipping.)")
            continue

        print(f"---- Processing {dir} ----")

        print("1. Converting PDFs to markdown (this may take a moment)...")
        extract_all_pdf_texts(dir)

        print("2. Extracting figures from PDFs...")
        extract_all_figures(dir)

        print("3. Running vector store operator...")
        vectorize_data(dir)

        print("4. Deleting .md and .pdf files...")
        for f in os.listdir(dir):
            if f.lower().endswith(".pdf") or f.lower().endswith(".md"):
                os.remove(os.path.join(dir, f))
        
        print(f"✔ Completed {dir}")

def delete_datasets(model_dir: str):
    """Deletes specified datasets from a course model. The specified datasets are retrieved from the last request form.

    Args:
        model_dir (str): The directory containing the model's data.
    """
    to_delete = request.form.getlist('delete_datasets[]')
    for dataset in to_delete:
        group_path = os.path.join(model_dir, secure_filename(dataset))
        if os.path.exists(group_path) and os.path.isdir(group_path):
            shutil.rmtree(group_path)

def remove_class_model(upload_root: str, course_id: str):
    """Removes a course model from the root bot data directory.

    Args:
        upload_root (str): The root directory where all course models are created and modified.
        course_id (str): The code used to identify the class.

    Raises:
        NotADirectoryError: If the model's directory does not exist/cannot be found.
    """
    print(f"Removing {course_id} from {upload_root} directory...")
    class_path = os.path.join(upload_root, course_id)
    try:
        if not os.path.isdir(class_path):
            raise NotADirectoryError(f"Unable to find directory {class_path}")
        shutil.rmtree(class_path)
        print(f"Successfuly removed {course_id}.")
    except Exception as e:
        print(f"Unable to remove {course_id}: {e}")

def load_rules(bot_path: str) -> list[str]:
    """Loads the rules for a course from the model's 'bot.txt' file.

    Args:
        bot_path (str): The path of the model's 'bot.txt' file.

    Returns:
        list[str]: A list of the model's rules.
    """
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
    
    return rules

def load_datasets(model_dir: str) -> list[str]:
    """Loads the names of a course model's existing datasets.

    Args:
        model_dir (str): The directory containing the model's data.

    Returns:
        list[str]: The names of the model's datasets.
    """
    datasets = sorted([
        d for d in os.listdir(model_dir)
        if os.path.isdir(os.path.join(model_dir, d)) and d != '__pycache__'
    ])

    return datasets