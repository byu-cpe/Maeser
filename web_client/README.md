# General Overview #
The web_client folder contains an update to the project in the form of a web-based editor for class data.

When fully flushed out, this would be implemented as more than a editor alone, but also a way to set up keys for different services, like discord. 

The folder is comprised of a few files:
- `static` & `templates` are used for the flask app display to the user. These come with all standard flask based projects.
- `doc_chunker_operator.py`, `rename_files.py`, & `extract_figures.py` are all necessary for file modification and manipulation. They are used by the local Makefile, intended to manipulate files that are uploaded and store them in the `bot_data` directory.
- `flask_webserver.py` is the main executable python file. This runs the flask web app.
- `Makefile` is usseful for the reasons stated earlier. It is run any time a change is made, wether that be a new dataset or an existing one.