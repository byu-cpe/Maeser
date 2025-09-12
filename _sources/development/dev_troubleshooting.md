# Dev Troubleshooting Guide

This page helps you diagnose and resolve common issues encountered during Maeser development and usage.

---

## Environment & Installation Issues

### Virtual Environment Activation

- **Symptom:** `python` or `pip` commands refer to system Python, not your `.venv`.
- **Solution:** Ensure you activate correctly:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows PowerShell: `.venv\Scripts\Activate.ps1`
  - Verify with `which python` (Unix), `Get-Command python` (Windows PowerShell), or `where.exe python` (Windows CMD). See also [**Check if the Virtual Environment is Active**](./development_setup.md#check-if-the-virtual-environment-is-active).

### Dependency Conflicts

- **Symptom:** `pip install -e .` fails, or `ModuleNotFoundError` for installed packages.
- **Solution:**
  1. Remove and recreate `.venv`:

     ```bash
     deactivate
     rm -rf .venv
     python3.10 -m venv .venv
     source .venv/bin/activate
     pip install -e .
     ```

  2. Run `poetry lock` then `poetry install --all-extras` to re-install dependencies.

---

## Configuration & API Key Problems

### Missing OpenAI API Key

- **Symptom:** `InvalidRequestError` or LLM calls fail silently.
- **Solution:**
  - For scripts that use `config.py` (such as the examples in `example/apps/`) verify that OpenAPI key is set in `config.yaml`, like so: `OPENAI_API_KEY: "<your-key>"`
  - For scripts that do not use `config.py` (such as `example/tools/embeddings_example.py`), set your OpenAPI key as an environment variable.
    Linux/MacOS:

    ```bash
    # Set the environment variable
    $ export OPENAI_API_KEY="<your-key>"

    # Confirm it was properly assigned
    $ $echo $OPENAI_API_KEY
    <your-key>
    ```

    Windows (Powershell):

    ```powershell
    # Set the environment variable
    PS> $Env:OPENAI_API_KEY = '<your-key>'
    
    # Confirm it was properly assigned
    PS> echo $Env:OPENAI_API_KEY
     <your-key>
    ```

### Incorrect Paths in `config.yaml`

- **Symptom:** `FileNotFoundError` for vector stores or log directories.
- **Solution:**
  1. Look for the following line in your terminal that prints when you start your Maeser application:
  
    ```text
    Using configuration at path/to/config.yaml (Priority 0)
    ```

    Ensure that `path/to/config.yaml` is the expected path for your `config.yaml` file. If the path is incorrect, open `config.py` and ensure your `config.yaml` file is located at one of the `config_paths`.

  1. Verify the following fields point to existing locations:
      - `vec_store_path`
      - `log_source_path`
      - `chat_history_path`
      - `accounts_db_path`

---

## Vector Store & Embedding Issues

### Empty or Irrelevant Retrievals

- **Symptom:** RAG returns unrelated or blank responses.
- **Solution:**
  1. In your `chat_logs/chat_history/`, check the `context` field in your chat logs and verify that context is being retrieved from your vector stores.
  1. If your application is using **Universal RAG**, the chatbot skip context retrieval if no vectorstores are relevant. Check the names of your vectorstores and make sure they are descriptive to their respective topics to ensure that they are properly retrieved.
  1. Confirm your vector store directories are correct and contain `index.faiss` and `index.pkl` files.
  1. Check your embedding step (e.g. in your script for [**embedding new content**](embedding)):

     ```python
     from langchain.embeddings.openai import OpenAIEmbeddings
     embeddings = OpenAIEmbeddings()
     ```

     Ensure embeddings have completed without errors.
  1. Experiment with `chunk_size` / `chunk_overlap` in `RecursiveCharacterTextSplitter`.

### FAISS Index/Vector Store Load Failures

- **Symptom:** Errors loading FAISS index (`IOError`, `faiss` exceptions).
- **Solution:**
  - Ensure that your rag graphs (e.g. `get_universal_rag`) are configured with the correct paths to your FAISS vector stores.
  - Confirm directory permissions: `chmod -R u+rw <vectorstore_folder>`.

---

## Testing & Documentation Build Failures

### PyTest Errors

- **Symptom:** `pytest tests` fails with import or assertion errors.
- **Solution:**
  - Ensure editable install: `pip install -e .`
  - Run pytests with verbose printing (on project root): `make testVerbose`
  - Run individual tests to isolate failures: `pytest tests/test_module.py::test_function`

### Sphinx Build Errors

- **Symptom:** `make html` errors on missing references or invalid syntax.
- **Solution:**
  1. Confirm that your [virtual environment](#virtual-environment-activation) is activated.
  2. Install docs extras: `make deps` (from `sphinx-docs/` directory) or `poetry install --only dev`
  3. Ensure that all cross-references in your `.md` / `.rst` files are correct.

### Sphinx TOCTree Warnings

- **Symptom:** Building the documentation yields one or more warnings that say, `WARNING: document isn't included in any toctree`.
- **Solution:**
  - Check `index.rst` and make sure that the document has been included in the table of contents.

---

## Flask & Web Interface Issues

### Server Won’t Start

- **Symptom:** `Address already in use` or `ModuleNotFoundError` for controllers.
- **Solution:**
  - Change port: in `app.run(port=...)`.
  - Verify `example/flask_example_user_management.py` uses correct imports and path.

### Authentication Failures

- **Symptom:** GitHub OAuth redirect errors or LDAP bind failures.
- **Solution (GitHub):**
  1. In GitHub OAuth App settings, ensure that **Homepage URL** matches the url of your app and that **Authorization callback URL** matches `github_callback_uri` in `config.py`.
  2. Check `github_client_id` and `github_client_secret` are correct.

- **Solution (LDAP):**
  1. Verify LDAP URLs, base DN, and search filters in config.
  2. Test binding with an LDAP client (e.g., `ldapsearch`).

---

## WSL Troubleshooting

### WSL File Permissions

- **Symptom:** Permission denied when accessing Windows files.
- **Solution:**
  - Use `chmod` to grant permissions.
  - If your project is set up in the Windows file system (`mnt/c/...`), consider moving it to the Linux file system (`~/projects/...`). Be sure to run `make clean_venv` and `make setup` after you do this to reconfigure your virtual environment.

---

## Getting Help

- **GitHub Issues:** Check for issues on the [**Maeser repository**](https://github.com/byu-cpe/Maeser/issues) or open a new one.
- **Community Contributions:** Submit documentation fixes or feature requests via a Pull Request.
