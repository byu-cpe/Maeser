# User Guide: Getting Started with Maeser

This guide is designed for users who want to use Maeser’s chatbot capabilities without diving into development. You will learn how to install Maeser, configure it via a simple YAML file, and run the provided **web** and **terminal** chat interfaces with minimal technical overhead.

---

## Prerequisites

- **Python 3.10+** installed on your system.
- Basic command-line familiarity (opening a terminal or PowerShell window).

---

## Install Maeser

Open a terminal (macOS/Linux) or PowerShell (Windows) and run:

```bash
pip install maeser
```

This command downloads the latest Maeser release and its dependencies from PyPI.

---

## Download Examples from GitHub

Navigate to the [**Maeser GitHub repository**](https://github.com/byu-cpe/Maeser) and download everything within the [`example/`](https://github.com/byu-cpe/Maeser/tree/main/example) directory into your project directory. Your project's folder structure should now contain:

```
.
├── config.py
├── config_template.yaml
├── create_byu_vectorstore.py
├── create_maeser_vectorstore.py
├── embeddings_example.py
├── flask_multigroup_example.py
├── flask_multigroup_example_user_management.py
├── flask_pipeline_example.py
├── flask_pipeline_example_user_management.py
├── requirements.txt
├── terminal_multigroup_example.py
├── terminal_pipeline_example.py
├── static
│   └── ...
└── vectorstores
    ├── maeser
    │   ├── index.faiss
    │   └── index.pkl
    └── byu
        ├── index.faiss
        └── index.pkl
```

---

## Prepare Configuration

Maeser uses a simple **YAML** file (`config.yaml`) to configure settings like API keys and file paths. You only need to do this once.

First, **make a copy of `config_template.yaml` and name it `config.yaml`.** You will populate the latter file with the necessary keys and configuration for your Maeser app.

Next, **Open `config.yaml`** in a text editor and update only these fields:

```yaml
OPENAI_API_KEY: "<your-openai-key>"
VEC_STORE_PATH: "vectorstores"
CHAT_HISTORY_PATH: "chat_logs"
USERS_DB_PATH: "users.db"
LLM_MODEL_NAME: "gpt-4o"
```

- If you don’t have an OpenAI key, you can sign up at [https://platform.openai.com/signup](https://platform.openai.com/signup).  
- The default paths (`vectorstores`, `chat_logs`, `users.db`) are relative to your working directory.

---

## A Note on the Example Vectorstores

The Maeser chatbot uses pre-built databases called **vectorstores** to retrieve knowledge. Each vectorstore is a directory containing an `index.faiss` and an `index.pkl` file. The Maeser GitHub repository contains two example vectorstores, **Maeser** and **BYU**. The example applications in this project are already configured to use these two vectorstores when the chatbot interacts with users.

---

## Choose one of the Example Flask Apps

Maeser uses a program called [**Flask**](https://flask.palletsprojects.com/en/stable/) to render its web chat interface. There are several example Flask apps to choose from; if you are choosing an example for the first time, start with either [`flask_multigroup_example.py`](https://github.com/byu-cpe/Maeser/blob/main/example/flask_multigroup_example.py) or [`flask_pipeline_example.py`](https://github.com/byu-cpe/Maeser/blob/main/example/flask_pipeline_example.py), based on your preferences:

- [`flask_multigroup_example.py`](https://github.com/byu-cpe/Maeser/blob/main/example/flask_multigroup_example.py) contains **separate chat branches** for each vectorstore.
- [`flask_pipeline_example.py`](https://github.com/byu-cpe/Maeser/blob/main/example/flask_pipeline_example.py) contains **one chat branch** that uses both vectorstores.

---

## Run the Web Chat Interface

1. **Run the web app** by executing the following in your terminal:
   
   ```bash
   python flask_multigroup_example.py
   ```

   or if you are using `flask_pipeline_example.py`:
   ```bash
   python flask_pipeline_example.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:3002
   ```

3. **Select a knowledge branch** (e.g., "Karl G. Maeser History", "BYU History", or "pipeline") and start chatting!

---

## Running the Terminal Chat Interface

For quick, command‑line access without a web browser, **Run one of the terminal scripts** by executing the following in your terminal:

   ```bash
   python terminal_multigroup_example.py
   ```

   or if you prefer to use `terminal_pipeline_example.py`:

   ```bash
   python terminal_pipeline_example.py
   ```

---

## Customizing Your Experience

- **Add Your Own Content:** Follow the guide at [**Embedding New Content**](../development/embedding.md) to embed your own documents as vectorstores. 
- **Customize the Web Interface:** Change the parameters of the **App_Manager** in your Flask script to change the color and icons used by the web interface. (For more information on the App_Manager class, refer to the source code documentation on [blueprints](../autodoc/maeser/maeser.blueprints.rst)).
- **Add Authentication:** Download one of the `flask_*_user_management_example.py` scripts to configure GitHub or LDAP authentication. See [**User Management Setup**](../development/flask_example.md#user-management-setup) in the **Maeser Example (with Flask & User Management)** documentation page for instructions on how to configure authentication.

---

## Getting Help  
- **GitHub Issues:** Report bugs or ask questions at [https://github.com/byu-cpe/Maeser/issues](https://github.com/byu-cpe/Maeser/issues).  


