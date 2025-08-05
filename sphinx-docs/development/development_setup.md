# Development Setup

This guide walks you through setting up a Maeser development environment from scratch. You’ll learn how to clone the repository, configure your Python environment, install dependencies, run tests, and build the docs.

---

## Prerequisites

- **Python 3.10+**
- **Git**
- **Make** (on macOS/Linux) or **Make for Windows** (e.g. via Git Bash)
- **[Poetry](https://python-poetry.org/) (Optional):** for dependency management
- **WSL (Recommended for Windows):** Windows Subsystem for Linux. See **[Windows Setup (WSL)](#windows-setup-wsl)** below.

---

## Clone the Repository

```bash
git clone https://github.com/byu-cpe/Maeser.git
cd Maeser
```

This gives you the latest `main` branch of the Maeser source code and examples.

---

## Create and Activate a Virtual Environment

Python comes with a module named **venv** that provides support for creating and activating virtual environments. **Maeser's top-level Makefile will create a new virtual environment if one does not exist, so this step can be skipped;** however, some basic information about virtual environments is provided if you choose to create one manually or are unfamiliar with venv.

> **Note:** `make setup` creates the virtual environment but does not activate it. You will still need to activate and deactivate the virtual environment manually within the project.

### Creating the Virtual Environment

To create the virtual environment, execute this command (at the root directory of your project):

```bash
python3 -m venv .venv
```

All of the packages and resources used by the virtual environment will be stored in the `.venv/` directory.

### Activating the Virtual Environment

To activate the virtual environment, execute one of the following commands, based on your operating system:

```bash
# For Linux and Mac
source .venv/bin/activate
```

```powershell
# For Windows (in Powershell window)
.venv\Scripts\Activate.ps1
```

### Check if the Virtual Environment is Active

Most shells will indicate if a Python virtual environment is active by appending `(.venv)` to the command prompt:

```{code-block} bash
:class: no-copybutton
(.venv) user@host:~/project/dir$
```

If you are unsure if your virtual environment is active, check the location of the Python executable via `which` (Linux/Mac) or `where.exe` (Windows):

```bash
# For Linux and Mac
$ which python
~/project/dir/.venv/bin/python
```

```powershell
# For Windows
> where.exe python
C:\project\dir\.venv\Scripts\python.exe
# Other locations of python.exe may appear below
```

If the location of Python is inside your `.venv/` directory, then your virtual environment is active.

### Deactivating the Virtual Environment

You can deactivate your virtual environment any time by executing the following command:

```bash
deactivate
```

---

## Install Maeser & Dependencies Using the Makefile

The top-level Makefile can be used to set up Maeser with its dependencies:

```bash
make setup
```

This will:

1. **Verify that a venv exists.** If no virtual environment is found, a new one will be created in the `venv/` directory.
2. **Install poetry** (used for package management).
3. **Install Maeser's dependencies** using poetry.
4. **Install development dependencies** (including Sphinx, pytest, etc.).
5. **Install the editable Maeser package** (`pip install -e .`).
6. **Run the pytests** to verify everything is working.

If you are having issues, try running each line from the Makefile's setup individually in your terminal:

```bash
source .venv/bin/activate # Activate your virtual environment
pip install poetry # Install poetry for package management
poetry lock # Update list of dependencies
poetry install --all-extras # Install all dependencies, including development dependencies
pip install -e . # Install Maeser in editable mode
pytest tests # Run the pytests
```

The top-level Makefile also comes with the following recipes:

- **`setup`:** As explained above.
- **`clean_venv`:** Removes the `.venv/` directory and its contents. If you need to reset and rebuild your environment, run this recipe first before running `make setup`.
- **`test`:** Runs the pytests to verify everything is working.
- **`testVerbose`:** Runs the pytests with verbose printing.

---

## Environment Configuration

Maeser uses a small configuration file for API keys, file paths, and settings.

First, **make a copy of `example/apps/config_template.yaml` and name it `config.yaml`.** You will populate the latter file with the necessary keys and configuration for your Maeser app.

Next, **update the following parameters in `config.yaml`**:

```{code-block} yaml
:class: no-copybutton
OPENAI_API_KEY: "your-openai-key-here"
# (Optional) GitHub OAuth Client ID/Secret if you plan to enable login
GITHUB_CLIENT_ID: ""
GITHUB_CLIENT_SECRET: ""
# (Optional) Other settings (e.g., vector store path, LDAP server details, etc.)
```

---

## Running Tests

Validate your setup by running:

```bash
pytest tests
```

Or simply:

```bash
make test
```

All tests should pass before you start making changes.

---

## Building the Documentation

Maeser’s documentation uses **Sphinx** (with **MyST** for Markdown support). To build the HTML site locally, navigate to the `sphinx-docs/` directory and execute the following:

```bash
make html
```

When the process finishes, open `sphinx-docs/_build/html/index.html` in your browser to view the documentation.

---

## Run the Example Scripts

Several working example scripts can be found in the `example/apps/` directory. To run these examples locally, see [**Maeser Example (with Flask & User Management)**](flask_example.md).

You’re all set!
If you run into any issues, refer to the [**Dev Troubleshooting Guide**](dev-troubleshooting.md).

---

## Windows Setup (WSL)

If you’re on Windows, we recommend using [**WSL (Windows Subsystem for Linux)**](https://learn.microsoft.com/en-us/windows/wsl/install) for a smoother experience. WSL enables you to run the Maeser project in a Linux-powered shell, ensuring the best compatibility with the project's Makefiles and dependencies. For instructions on how to set up Maeser in WSL, see [**Development Setup with WSL (Windows Subsystem for Linux)**](wsl_development).

---

## Additional Tips

- **Hot-reload during development**: Run the Flask example in [**debug mode**](flask_example.md#enable-debug-mode-optional) to auto-restart on code changes.
- **IDE integration**: Point your IDE’s interpreter to the `.venv` for linting and Intellisense.
