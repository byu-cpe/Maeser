# Development Setup

This guide walks you through setting up a Maeser development environment from scratch. You’ll learn how to clone the repository, configure your Python environment, install dependencies, run tests, build the docs, and (optionally) set up on Windows via WSL.

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

## Create & Activate a Virtual Environment

You have two options: use plain `venv`, or Poetry.

### Using `venv`

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate
```

```powershell
# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### Using Poetry

```bash
# Install Poetry if you haven't already
pip install poetry

# Let Poetry install dependencies and activate venv
poetry install
poetry shell
```

---

## Install Maeser & Dependencies

Once your virtual environment is active:

### Editable Install (for development)

```bash
pip install -e .
```

This installs Maeser in “editable” mode so that changes you make locally take effect immediately.

### Install All Requirements via Make

A convenient shortcut:

```bash
make setup
```

This will:

1. Install the editable package (`pip install -e .`)
2. Install development dependencies (including Sphinx, pytest, etc.)
3. Run the test suite once to verify everything is working

---

## Environment Configuration

Maeser uses a small configuration file for API keys, file paths, and settings.

Open `config_example.yaml` and set:
```yaml
OPENAI_API_KEY: "your-openai-key-here"
# (Optional) GitHub OAuth Client ID/Secret if you plan to enable login
GITHUB_CLIENT_ID: ""
GITHUB_CLIENT_SECRET: ""
# (Optional) Other settings (e.g., vectorstore paths, LDAP server details, etc.)
```
**Environment variables** are also supported:
```bash
export OPENAI_API_KEY="your-openai-key-here"
```

> **Note:**  
> For deployment, it is recommended, although not required, that you copy the provided files in the `/example/` directory as opposed to modifying them directly. Make a copy of `config_example.py` and rename it to `config.yaml`:
>    ```bash
>    cp config_example.yaml config.yaml
>    # Edit config.yaml with production API keys, paths, and DB credentials
>    ```
>
> Then in "config_example.py", be sure to update the config paths:
> ```python
>     config_paths = [
>         'config.yaml',
>         './config.yaml',
>         'example/config.yaml'
>         # Or anywhere else you plan on storing config.yaml
>     ]
> ```
> 
> Be sure to rename the other example files and update their references accordingly.

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

Maeser’s docs use Sphinx (with MyST for Markdown support). To build the HTML site locally:

```bash
cd sphinx-docs
make html
```

Then open `sphinx-docs/build/html/index.html` in your browser.

---

## Windows Setup (WSL)

If you’re on Windows, we recommend using **[WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install)** for a smoother experience. WSL enables you to run the Maeser project in a Linux-powered shell, ensuring the best compatibility with the project's makefiles and dependencies. For instructions on how to set up Maeser in WSL, read **[Development Setup with WSL (Windows Subsystem for Linux)](wsl_development)** in the documentation.

---

## Additional Tips

- **Hot-reload during development**: Run the Flask example in debug mode to auto-restart on code changes.
- **IDE integration**: Point your IDE’s interpreter to the `.venv` or Poetry venv for linting and Intellisense.
- **Keep your branches tidy**: Create a feature branch for each change and open a PR against `main`.
- **Update docs as you code**: If you add or modify functionality, update the corresponding `.md` or `.rst` file in `sphinx-docs/source/`.

---

You’re all set!
If you run into any issues, check existing GitHub issues or open a new one.

