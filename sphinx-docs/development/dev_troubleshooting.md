# Dev Troubleshooting Guide

This page helps you diagnose and resolve common issues encountered during Maeser development and usage.

---

## Environment & Installation Issues

### Virtual Environment Activation

- **Symptom:** `python` or `pip` commands refer to system Python, not your `.venv`.
- **Solution:** Ensure you activate correctly:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows PowerShell: `.venv\Scripts\Activate.ps1`
  - Verify with `which python` (Unix), `Get-Command python` (Windows PowerShell), or `where.exe python` (Windows CMD).

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
  - For scripts that use `config.py` verify that OpenAPI key is set in `config.yaml`, like so: `OPENAI_API_KEY: "<your-key>"`
  - For scripts that do not use `config.py` verify that OpenAPI key is set as an environment variable:

    ```bash
    export OPENAI_API_KEY="<your-key>"
    ```

  Confirm with `echo $OPENAI_API_KEY` (Unix) or `echo %OPENAI_API_KEY%` (Windows).

### Incorrect Paths in `config.yaml`

- **Symptom:** `FileNotFoundError` for vector stores or log directories.
- **Solution:** Verify the following fields point to existing locations:
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
  2. Confirm your FAISS index directories are correct and contain `index.faiss` and `index.pkl` files.
  3. Check your embedding step (e.g. in your script for [**embedding new content**](embedding)):

     ```python
     from langchain.embeddings.openai import OpenAIEmbeddings
     embeddings = OpenAIEmbeddings()
     ```

     Ensure embeddings have completed without errors.
  4. Experiment with `chunk_size` / `chunk_overlap` in `RecursiveCharacterTextSplitter`.

### Index Load Failures

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
  - Check `index.rst` and make sure that the file has been included in the table of contents.

---

## Flask & Web Interface Issues

### Server Won’t Start

- **Symptom:** `Address already in use` or `ModuleNotFoundError` for controllers.
- **Solution:**
  - Change port: in `app.run(port=...)` or export `FLASK_RUN_PORT`.
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

## WSL & Docker Troubleshooting

### WSL File Permissions

- **Symptom:** Permission denied when accessing Windows files.
- **Solution:**
  - Access project via the Linux filesystem (`~/projects/Maeser`), not `/mnt/c/...`.
  - Use `chmod` to grant permissions.

---

## Getting Help

- **GitHub Issues:** Check for issues on the [Maeser repository](https://github.com/byu-cpe/Maeser/issues) or open a new one.
- **Community Contributions:** Submit documentation fixes or feature requests via a Pull Request.
