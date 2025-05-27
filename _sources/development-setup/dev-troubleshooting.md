# Dev Troubleshooting Guide

This page helps you diagnose and resolve common issues encountered during Maeser development and usage.

---

## Environment & Installation Issues

### Virtual Environment Activation
- **Symptom:** `python` or `pip` commands refer to system Python, not your `.venv`.
- **Solution:** Ensure you activate correctly:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows PowerShell: `.venv\Scripts\Activate.ps1`
  - Verify with `which python` (Unix) or `Get-Command python` (PowerShell).

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
  2. If using Poetry, run `poetry lock` then `poetry install`.

### FAISS Installation Errors
- **Symptom:** Errors compiling FAISS on Windows or macOS.
- **Solution:**
  - **Windows:** Use WSL2 or install `faiss-cpu` via Conda:
    ```bash
    conda install -c conda-forge faiss-cpu
    ```
  - **macOS/Linux:** Ensure you have `cmake` & `gcc` installed (`sudo apt install build-essential cmake`).

---

## Configuration & API Key Problems

### Missing OpenAI API Key
- **Symptom:** `InvalidRequestError` or LLM calls fail silently.
- **Solution:**
  - In `config.yaml`, set `OPENAI_API_KEY: "<your-key>"`, or export:
    ```bash
    export OPENAI_API_KEY="<your-key>"
    ```
  - Confirm with `echo $OPENAI_API_KEY` (Unix) or `echo %OPENAI_API_KEY%` (Windows).

### Incorrect Paths in `config_example.yaml`
- **Symptom:** FileNotFoundError for vectorstores or log directories.
- **Solution:** Verify the following fields point to existing locations:
  - `vec_store_path`
  - `log_source_path`
  - `chat_history_path`
  - `accounts_db_path`

---

## Vectorstore & Embedding Issues

### Empty or Irrelevant Retrievals
- **Symptom:** RAG returns unrelated or blank responses.
- **Solution:**
  1. Confirm your FAISS index directories are correct and contain `.index` files.
  2. Check your embedding step (e.g. in your script for [embedding new content](embedding)):
     ```python
     from langchain.embeddings.openai import OpenAIEmbeddings
     embeddings = OpenAIEmbeddings()
     ```
     Ensure embeddings have completed without errors.
  3. Experiment with `chunk_size` / `chunk_overlap` in `RecursiveCharacterTextSplitter`.

### Index Load Failures
- **Symptom:** Errors loading FAISS index (`IOError`, `faiss` exceptions).
- **Solution:**
  - Ensure that your rag graphs (`get_simple_rag` or `get_pipeline_rag`) are configured with the correct paths to your FAISS vectorstores.
  - Confirm directory permissions: `chmod -R u+rw <vectorstore_folder>`.

---

## Testing & Documentation Build Failures

### PyTest Errors
- **Symptom:** `pytest tests` fails with import or assertion errors.
- **Solution:**
  - Ensure editable install: `pip install -e .`
  - Run individual tests to isolate failures: `pytest tests/test_module.py::test_function`

### Sphinx Build Errors
- **Symptom:** `make html` errors on missing references or invalid syntax.
- **Solution:**
  1. Confirm that your [virtual environment](#virtual-environment-activation) is activated.
  2. Install docs extras: `pip install -e .[docs]` or `pip install myst-parser`
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
  - Verify `example/flask_example_user_mangement.py` uses correct imports and path.

### Authentication Failures
- **Symptom:** GitHub OAuth redirect errors or LDAP bind failures.
- **Solution (GitHub):**
  1. In GitHub OAuth App settings, ensure **Authorization callback URL** matches `GITHUB_AUTH_CALLBACK_URI`.
  2. Check `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are correct.

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

### Docker Container Issues
- **Symptom:** Container fails to build or run Maeser.
- **Solution:**
  1. Ensure Dockerfile exposes necessary ports and mounts volumes:
     ```Dockerfile
     COPY . /app
     WORKDIR /app
     RUN pip install -e .
     EXPOSE 3002
     CMD ["python", "example/flask_example_user_mangement.py"]
     ```
  2. Use `docker-compose.yml` for multi-container setups (e.g., database).  

---

## Getting Help

- **GitHub Issues:** Check for existing issues or open a new one: https://github.com/byu-cpe/Maeser/issues
- **Community Contributions:** Submit documentation fixes or feature requests via a Pull Request.

