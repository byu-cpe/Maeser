# The dynamic_implementations Directory

This directory is intended currently to run the code in dynamic outlets, like discord.

Ideally, we can push some of these into the Maeser package, but there are a few things in the way at the moment:

- The `generate_response.py` could be moved, but requires things like keys and tokens to be defined. It currently gets those from the `config.yaml` in this folder, but may be set up as variables that are defined in another way.
- the `_handler.py` scripts are also independent, and are intended to be the executable scripts, run in separate threads or processes, that allow interaction with the various outlets. If moved into the package, they would need to be able to run on independent processes. through an external script or the like.
- `bot_data` is accessed by the handlers and the `generate_response.py`. This folder would need to stay outside the package, and is defined by administrators. This can probably move into the admin_portal folder, but would require some refactoring.
- `static` and `templates` are used by the webapp_handler currently, which is a flask app. This may need to be altered as well.
- `chat_logs` should also be accessed by administrators and users, not a part of the package.
