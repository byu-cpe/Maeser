# The Admin Portal

The `admin_portal/` directory contains an update to the project in the form of a web-based editor for class data.

When fully flushed out, this would be implemented as more than a editor alone, but also a way to set up keys for different services, like discord.

The folder is comprised of a few files:

- `flask_admin_portal.py` is the main executable python file. This runs the flask web app. This should be executed while in the `admin_portal/` directory.
- `config.py` is used to locate `config.yaml` and expose its values for use by the web server. It looks for `config.yaml` in `../dynamic_implementations/config.yaml` by default.
- `static` & `templates` are used for the flask app display to the user. These come with all standard flask based projects.
- `design_model.py` contains the code that handles generating and editing class models.
- `extract_text.py`, `extract_figures.py`, and `vector_store_operator.py` are necessary for file modification and manipulation. They are used by the local `design_model.py`, intended to manipulate files that are uploaded and store them in the `bot_data` directory.
