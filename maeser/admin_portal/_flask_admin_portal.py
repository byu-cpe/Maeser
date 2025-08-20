# SPDX-License-Identifier: LGPL-3.0-or-later

from flask import Flask, render_template, request, redirect, url_for, session
from maeser.config import VEC_STORE_PATH as UPLOAD_ROOT, OPENAI_API_KEY
import os
import functools
import secrets
from werkzeug.utils import secure_filename
from maeser.admin_portal.design_model import (
    get_model_config,
    save_model,
    delete_datasets,
    remove_class_model,
    load_rules,
    load_datasets,
)

admin_flask_app: Flask = Flask(__name__)

# All code below is for the FLASK INTERFACE
# Demo User
# The values of "username" and "password" will be replaced when run_admin_portal() is called
USER = {"username": "adam", "password": "ajosiahs", "is_admin": True}

# Global Variables
model_name = ""
host_address = ""
rules = []
contexts = []


# decorator for login checking
def require_login(func):
    @functools.wraps(
        func
    )  # updates metadata so that check_login.__name__ == func.__name__
    def check_login(*args, **kwargs):
        if "user" in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return check_login


@admin_flask_app.route("/")
@require_login
def home():
    return render_template("admin_portal.html", username=session["user"])


@admin_flask_app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USER["username"] and password == USER["password"]:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            error = "Invalid Credentials. Please try again."
    return render_template("login.html", error=error)


@admin_flask_app.route("/design_model", methods=["GET", "POST"])
@require_login
def design_model():
    if request.method == "POST":
        # Get model config
        try:
            model_config: tuple = get_model_config(UPLOAD_ROOT)
        except AttributeError as e:
            print(f"Unable to use model config: {e}")
            return redirect(url_for("design_model"))

        # Save model
        try:
            save_model(UPLOAD_ROOT, *model_config)
        except Exception as e:
            print(f"Unable to generate model: {e}")
            return redirect(url_for("design_model"))

        print(
            "Model generation complete. Please check the terminal output to ensure no errors were thrown."
        )
        return redirect(url_for("manage_models"))

    return render_template("design_model.html", username=session["user"])


@admin_flask_app.route("/manage_models", methods=["GET", "POST"])
@require_login
def manage_models():
    if request.method == "POST":
        course_id = request.form.get("course_id")
        if not course_id:
            print("Error: Course ID is required.")
            return redirect(url_for("design_model"))
        else:
            remove_class_model(UPLOAD_ROOT, course_id)
        return redirect(url_for("manage_models"))

    # List all course_id folders inside UPLOAD_ROOT
    models = []
    for item in os.listdir(UPLOAD_ROOT):
        model_path = os.path.join(UPLOAD_ROOT, item)
        if os.path.isdir(model_path):
            models.append(item)  # item is the course_id

    return render_template(
        "manage_models.html", username=session["user"], models=models
    )


@admin_flask_app.route("/edit_model/<course_id>", methods=["GET", "POST"])
@require_login
def edit_model(course_id):
    # Get important file paths
    model_dir = os.path.join(UPLOAD_ROOT, secure_filename(course_id))
    bot_path = os.path.join(model_dir, "bot.txt")

    if request.method == "POST":
        # Get model config
        try:
            model_config: tuple = get_model_config(UPLOAD_ROOT)
        except AttributeError as e:
            print(f"Unable to use model config: {e}")
            return redirect(url_for("edit_model", course_id=course_id))

        # Delete selected datasets
        delete_datasets(model_dir)

        # Save model
        try:
            save_model(UPLOAD_ROOT, *model_config)
        except Exception as e:
            print(f"Unable to generate model: {e}")
            return redirect(url_for("edit_model", course_id=course_id))
        
        print(
            "Model generation complete. Please check the terminal output to ensure no errors were thrown."
        )
        return redirect(url_for("manage_models"))

    # Get rules and datasets
    rules = load_rules(bot_path)
    current_datasets = load_datasets(model_dir)

    return render_template(
        "edit_model.html",
        course_id=course_id,
        rules=rules,
        current_datasets=current_datasets,
        username=session["user"],
    )


@admin_flask_app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


def _check_config_variables():
    """Checks to see if any necessary config values are unassigned and raises a LookupError
    accordingly.

    Necessary config values are pulled from `config.yaml` using **maeser.config** and are as follows:

    - **UPLOAD_ROOT** (*str*): The path where courses are accessed and managed by the admin portal. Defined in the "vectorstore:vec_store_path" field in the config.
    - **OPENAI_API_KEY** (*str*): The API key for the OpenAI LLM. Defined in the "api_keys:openai_api_key" field in the config.
    
    Raises:
        LookupError: If any of the necessary config values are unassigned.
    """
    if UPLOAD_ROOT == "" or UPLOAD_ROOT == "...":
        raise LookupError(f'vec_store_path ("{UPLOAD_ROOT}") cannot be unassigned.')

    if OPENAI_API_KEY == "" or OPENAI_API_KEY == "...":
        raise LookupError(f'openai_api_key ("{OPENAI_API_KEY}") cannot be unassigned.')


def run_admin_portal(
    username: str = "adam",
    password: str = "ajosiahs",
    secret_key: str | None = None,
    host: str | None = None,
    port: int | None = None,
    debug: bool | None = None,
    load_dotenv: bool = True,
    **options,
):
    """Runs the admin portal flask application.

    Allows a username, password, and secret key to be declared as well as all standard Flask.run parameters.
    See the Flask documentation for more information on parameters and options.

    In production, **username**, **password**, and **secret_key** should always be assigned.

    Args:
        username (str, optional): The username for logging in to the admin portal. Defaults to "adam".
        password (str, optional): The password for logging in to the admin portal. Defaults to "ajosiahs".
        secret_key (str, optional): The secret key to assign to the application. Creates a random key
            if none is provided.
        host (str | None, optional): The web server hostname.
        port (int | None, optional): The web server port.
        debug (bool | None, optional): If True, enables debug mode.
        load_dotenv (bool, optional): Loads .env and .flaskenv files to initialize environment
            variables. Defaults to True.
        options: Werkzeug server options. For more information, see ``werkzeug.serving.run_simple``.
    """
    _check_config_variables()

    # Assign parameters specific to Admin Portal
    USER["username"] = username
    USER["password"] = password
    admin_flask_app.secret_key = secret_key if secret_key else secrets.token_hex()

    # Run Flask with parameters
    admin_flask_app.run(
        host=host,
        port=port,
        debug=debug,
        load_dotenv=load_dotenv,
        **options,
    )


if __name__ == "__main__":
    run_admin_portal()
