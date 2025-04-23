# Development Setup

This guide walks you through setting up a Maeser development environment from scratch. You’ll learn how to clone the repository, configure your Python environment, install dependencies, run tests, build the docs, and (optionally) set up on Windows via WSL.

---

## Prerequisites

- **Python 3.10+**  
- **Git**  
- **Make** (on macOS/Linux) or **Make for Windows** (e.g. via Git Bash)  
- **Optional:** [Poetry](https://python-poetry.org/) for dependency management  
- **Optional (WSL):** Windows Subsystem for Linux, if you’re on Windows  

---

## 1. Clone the Repository

```bash
git clone https://github.com/byu-cpe/Maeser.git
cd Maeser
```

This gives you the latest `main` branch of the Maeser source code and examples.

---

## 2. Create & Activate a Virtual Environment

You have two options: use plain `venv` / `pip`, or Poetry.

### 2.1. Using `venv` + `pip`

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### 2.2. Using Poetry

```bash
# Install Poetry if you haven't already
pip install poetry

# Let Poetry install dependencies and activate venv
poetry install
poetry shell
```

---

## 3. Install Maeser & Dependencies

Once your virtual environment is active:

### 3.1. Editable Install (for development)

```bash
pip install -e .
```

This installs Maeser in “editable” mode so that changes you make locally take effect immediately.

### 3.2. Install All Requirements via Make

A convenient shortcut:

```bash
make setup
```

This will:
1. Install the editable package (`pip install -e .`)  
2. Install development dependencies (including Sphinx, pytest, etc.)  
3. Run the test suite once to verify everything is working  

---

## 4. Environment Configuration

Maeser uses a small configuration file for API keys, file paths, and settings.

1. Copy the example:
   ```bash
   cp config_example.yaml config.yaml
   ```
2. Open `config.yaml` and set:
   ```yaml
   OPENAI_API_KEY: "your-openai-key-here"
   # (Optional) GitHub OAuth Client ID/Secret if you plan to enable login
   GITHUB_CLIENT_ID: ""
   GITHUB_CLIENT_SECRET: ""
   # (Optional) Other settings (e.g., vectorstore paths, LDAP server details, etc.)
   ```
3. **Environment variables** are also supported:
   ```bash
   export OPENAI_API_KEY="your-openai-key-here"
   ```

---

## 5. Running Tests

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

## 6. Building the Documentation

Maeser’s docs use Sphinx (with MyST for Markdown support). To build the HTML site locally:

```bash
cd sphinx-docs
make html
```

Then open `sphinx-docs/build/html/index.html` in your browser.

---

## 7. Windows Setup (WSL)

If you’re on Windows, we recommend using WSL for a smoother experience:

1. Install WSL following Microsoft’s guide:  
   https://learn.microsoft.com/windows/wsl/install  
2. In your WSL terminal, follow **Steps 1–6** above as if on Linux.  
3. Use your WSL path (e.g., `/mnt/c/Users/you/Maeser`) for the cloned repo.

---

## 8. Additional Tips

- **Hot-reload during development**: Run the Flask example in debug mode to auto-restart on code changes.  
- **IDE integration**: Point your IDE’s interpreter to the `.venv` or Poetry venv for linting and Intellisense.  
- **Keep your branches tidy**: Create a feature branch for each change and open a PR against `main`.  
- **Update docs as you code**: If you add or modify functionality, update the corresponding `.md` or `.rst` file in `sphinx-docs/source/`.

## 9. Developer Tools & Troubleshooting

- **Linting & Formatting**: Use Black and Flake8 to maintain consistent code style. Install with `pip install black flake8` and consider setting up [pre-commit hooks](https://pre-commit.com/) to run them automatically.
- **Type Checking**: Integrate Mypy for static type verification by installing `pip install mypy` and running `mypy maeser/` as part of your development cycle.
- **Pre-commit Hooks**: Add a `.pre-commit-config.yaml` to configure hooks (e.g., black, flake8, isort) and install via `pre-commit install` for automated checks on commits.
- **Continuous Integration (CI)**: Configure GitHub Actions (or another CI provider) to run tests, linting, type checks, and documentation builds on each pull request to ensure code quality.
- **Docker Support** (Optional): Create a `Dockerfile` and `docker-compose.yml` to containerize Maeser and its dependencies, enabling reproducible environments and easy on-boarding for developers.
- **Troubleshooting Common Issues**:
  - **Missing API Keys**: Ensure `config.yaml` and environment variables (e.g., `OPENAI_API_KEY`) are set correctly.
  - **FAISS Installation Errors**: On Windows, use the WSL environment or install via `conda install -c conda-forge faiss-cpu` to avoid build issues.
  - **Permission Errors**: Verify file and directory permissions for log files, vectorstores, and the `config.yaml` file.
  - **Dependency Conflicts**: If you encounter version mismatches, recreate your virtual environment and pin dependencies in `pyproject.toml` or `requirements.txt`.
