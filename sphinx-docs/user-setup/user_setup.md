# User Guide: Getting Started with Maeser

This guide is designed for users who want to use Maeser’s chatbot capabilities without diving into development. You will learn how to install Maeser, configure it via a simple YAML file, and run the provided **web** and **terminal** chat interfaces with minimal technical overhead.

> **Note:** The following guide is for the Flask and terminal implementations of Maeser. For detailed instructions on setting up the Maeser Discord handler, see [Setting up a Discord Bot](./discord.md).

---

## Prerequisites

- **Python 3.10+** installed on your system.
- **Basic command-line familiarity** (opening a terminal or PowerShell window).
- **Python Virtual Environment (Optional but Recommended)**—Activating a virtual environment ensures that Maeser's dependencies are of the right version and will not interfere with packages installed system-wide. For reference on setting up a Python virtual environment, see [**Create and Activate a Virtual Environment**](../development/development_setup.md#create-and-activate-a-virtual-environment) in the Development Setup guide.

---

## Install Maeser

Open a terminal (macOS/Linux) or PowerShell (Windows) and run:

```bash
pip install maeser
```

This command downloads the latest Maeser release and its dependencies from PyPI.

---

## Download Example Resources from GitHub

Navigate to the [**Maeser GitHub repository**](https://github.com/byu-cpe/Maeser) and enter the [`example/`](https://github.com/byu-cpe/Maeser/tree/main/example) directory. This directory contains three folders:

```{code-block} none
:class: no-copybutton
example
├── apps
├── resources
├── tools
└── ...
```

To start, you will only need `apps/` and `resources/`. Download these two folders into your project directory. Your project should now have the following folder structure:

```{code-block} none
:class: no-copybutton
.
├── apps
│   ├── config.py
│   ├── config_template.yaml
│   ├── config.yaml
│   ├── pipeline
│   │   ├── flask_pipeline.py
│   │   ├── flask_pipeline_user_management.py
│   │   └── terminal_pipeline.py
│   ├── simple
│   │   ├── flask_simple.py
│   │   ├── flask_simple_user_management.py
│   │   └── terminal_simple.py
│   └── universal
│       ├── flask_universal_user_management.py
│       ├── flask_universal.py
│       └── terminal_universal.py
└── resources
    ├── static
    │   ├── Karl_G_Maeser.png
    │   └── LICENSE.EXAMPLE_RESOURCES.md
    └── vectorstores
        ├── byu
        │   ├── index.faiss
        │   └── index.pkl
        ├── LICENSE.VECTORSTORE.md
        └── maeser
            ├── index.faiss
            └── index.pkl
```

---

## Prepare Configuration

Maeser uses a simple **YAML** file (`config.yaml`) to configure settings like API keys and file paths. You only need to do this once.

First, **make a copy of `apps/config_template.yaml` and name it `config.yaml`.** You will populate the latter file with the necessary keys and configuration for your Maeser app.

Next, **open `apps/config.yaml`** in a text editor and update only these fields:

```{code-block} yaml
:class: no-copybutton
OPENAI_API_KEY: "<your-openai-key>"
VEC_STORE_PATH: "vectorstores"
CHAT_HISTORY_PATH: "chat_logs"
USERS_DB_PATH: "users.db"
LLM_MODEL_NAME: "gpt-4o"
```

- If you don’t have an OpenAI key, you can [sign up here](https://platform.openai.com/signup).  
- The default paths (`vectorstores`, `chat_logs`, `users.db`) are relative to your working directory.

---

## A Note on the Example Vector Stores

The Maeser chatbot uses pre-built databases called **vector stores** to retrieve knowledge. Each vector store is a directory containing an `index.faiss` and an `index.pkl` file. The Maeser GitHub repository contains two example vector stores, **Maeser** and **BYU**. The example applications in this project are already configured to use these two vector stores (found in `resources/vectorstores`) when the chatbot interacts with users.

> **Note:** To embed your own documents as vector stores, follow the guide at [**Embedding New Content**](../development/embedding.md) (after setting up Maeser). You will need to download `example/tools` from the repository to use the scripts in that guide.

---

## Choose one of the Example Flask Apps

Maeser uses a program called [**Flask**](https://flask.palletsprojects.com/en/stable/) to render its web chat interface. There are several example Flask apps to choose from, and each type of application is organized into one of three directories based on chatbot behavior:

- **`simple/`** contains scripts that separate each vector store into its own branch, forcing the chatbot to stick to one topic per conversation.
- **`pipeline/`** contains scripts that combine all vector stores into one chat branch, allowing the chatbot to dynamically choose the most relevant vector store when answering a user's question.
- **`universal/`** contains scripts that combine all vector stores into one chat branch, like the `pipeline/` scripts, but also allow the chatbot to pull from multiple vector stores when answering a user's question.

Pick the behavior of your choice, and choose one of the scripts to use for your application. If you are unsure which to choose, `universal/flask_universal.py` is recommended.

---

## Update the Path to `config.py`

By default, the Maeser app scripts look for `config.py` in `example/apps`. Since your project is structured differently, you will need to update this. Each of the example app scripts has the following line of code near the top of the file:

```python
from example.apps.config import (...)
```

Replace that line with the following:

```python
from apps.config import (...)
```

You will need to replace `example.apps.config` with `apps.config` within all example app scripts you plan on running. Many code editors have a find-and-replace feature that lets you do this trivially. If you are on Linux or Mac, you can also do this in the command line by running the following command within `apps/`:

```bash
sed -i 's/example\.apps\.config/apps\.config/g' **/*.py
```

---

## Run the Web Chat Interface

1. **Run the web app** by executing the following in your terminal (from the **root directory** of your project):

   ```bash
   python apps/universal/flask_universal.py
   ```

   replacing `universal/flask_universal.py` above with the script of your choice.

2. **Open your browser** and go to:

   ```none
   http://localhost:3002
   ```

3. **Select a knowledge branch** (e.g., "Karl G. Maeser History" or "BYU History") and start chatting!

---

## Running the Terminal Chat Interface

For quick, command‑line access without a web browser, **run one of the terminal scripts** by executing the following in your terminal:

   ```bash
   python apps/universal/terminal_universal.py
   ```

   replacing `universal/terminal_universal.py` with the terminal script of your choice.

---

## Next Steps

- **Add Your Own Content:** Follow the guide at [**Embedding New Content**](../development/embedding.md) to embed your own documents as vector stores. You will need to download `example/tools` from the repository to use the scripts in this guide.
- **Add Authentication:** Open one of the `flask_*_user_management.py` scripts to configure GitHub or LDAP authentication. See [**Configuring Authenticators**](../development/flask_example.md#configuring-authenticators) in the **Maeser Example (with Flask & User Management)** documentation page for instructions on how to configure authentication.
- **Customize the Web Interface:** Change the parameters of the **AppManager** in your Flask script to change the color and icons used by the web interface. (For more information on the AppManager class, refer to the source code documentation in the [**maeser.blueprints**](../autodoc/maeser/maeser.blueprints.rst) module.)
- **Deploy Your Maeser App:** Follow the [**Deployment Guide**](../sysadmin/deployment.md) to deploy your Maeser application as an HTTP server.

---

## Getting Help

- **GitHub Issues:** Report bugs or ask questions at [https://github.com/byu-cpe/Maeser/issues](https://github.com/byu-cpe/Maeser/issues).  
