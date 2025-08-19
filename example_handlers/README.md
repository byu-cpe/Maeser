# The example_handlers Directory

This directory contains the necessary file structure for running the Discord handler provided by [**maeser.discord_handler**](../maeser/discord_handler/_discord_handler.py).

Unlike the Flask implementations found in the `example/` directory which structure datasets by **vector store** (in `example/resources/vectorstores/`), the discord handler structures datasets by **course** (in `example_handlers/bot_data/`).

Use the **Admin Portal** to automatically create and structure courses by running `admin_portal/flask_admin_portal.py` **from within the `admin_portal/` directory.**
