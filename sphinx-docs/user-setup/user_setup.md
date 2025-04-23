# User Guide: Getting Started with Maeser

This guide is designed for users who want to **use** Maeser’s chatbot capabilities without diving into development. You will learn how to install Maeser, configure it via a simple YAML file, and run the provided **web** and **terminal** chat interfaces with minimal technical overhead.

---

## 1. Prerequisites

- **Python 3.10+** installed on your system (download from https://python.org).  
- Basic command‑line familiarity (opening a terminal or PowerShell window).  
- Internet access for installing packages and, optionally, for registering an OpenAI API key.  

> **Note:** No programming experience is required—follow the steps below to get started.

---

## 2. Install Maeser

Open a terminal (macOS/Linux) or PowerShell (Windows) and run:

```bash
pip install maeser
```

This command downloads the latest Maeser release and its dependencies from PyPI.

---

## 3. Prepare Configuration

Maeser uses a simple **YAML** file (`config.yaml`) to store settings like API keys and file paths. You only need to do this once.

1. **Copy the example file** (in the installation directory) to your working folder:
   ```bash
   cp $(python -c "import maeser; print(maeser.__file__)")/../config_example.yaml config.yaml
   ```
2. **Open `config.yaml`** in a text editor and update only these fields:
   ```yaml
   OPENAI_API_KEY: "<your-openai-key>"
   VEC_STORE_PATH: "./vectorstores"
   CHAT_HISTORY_PATH: "./chat_logs"
   USERS_DB_PATH: "./users.db"
   LLM_MODEL_NAME: "gpt-4o"
   ```
   - If you don’t have an OpenAI key, you can sign up at https://platform.openai.com/signup.  
   - The default paths (`./vectorstores`, `./chat_logs`, `./users.db`) work in your current folder.

> **Tip:** You can also set `OPENAI_API_KEY` as an environment variable to avoid editing `config.yaml`:
> ```bash
> export OPENAI_API_KEY="<your-openai-key>"
> ```

---

## 4. Download Example Vectorstores

Maeser requires pre-built vectorstores (FAISS indexes) to retrieve knowledge. For simplicity, download the **Maeser** and **BYU** vectorstores from the project’s GitHub releases:

1. Visit: https://github.com/byu-cpe/Maeser/releases/latest
2. Download `vectorstores-maeser.zip` and `vectorstores-byu.zip`.  
3. Unzip into your working folder:
   ```bash
   unzip vectorstores-maeser.zip -d vectorstores/maeser
   unzip vectorstores-byu.zip   -d vectorstores/byu
   ```

Your folder structure should now contain:
```
./config.yaml
./vectorstores/
    ├─ maeser/
    └─ byu/
```

---

## 5. Running the Web Chat Interface

Maeser provides a ready‑to‑use Flask web app with optional user authentication.

1. **Install extra requirements**:
   ```bash
   pip install maeser[web]
   ```
2. **Run the web app**:
   ```bash
   python -m maeser.webapp
   ```
3. **Open your browser** and go to:
   ```
   http://localhost:3002
   ```
4. **Select a knowledge branch** (e.g., "Karl G. Maeser History" or "BYU History") and start chatting!

> **Tip:** If you have a GitHub OAuth key in `config.yaml`, you can log in to manage user quotas.

---

## 6. Running the Terminal Chat Interface

For quick, command‑line access without a web browser:

```bash
python -m maeser.terminal
```
1. Select a branch from the numbered menu.  
2. Type your question and press **Enter**.  
3. Type `exit` or `quit` to end the session.

---

## 7. Customizing Your Experience

- **Add Your Own Content:** Follow the easy guide at `maeser.embedding` (no coding required) to embed your own documents.  
- **Switch Models:** Change `LLM_MODEL_NAME` in `config.yaml` to another model name supported by OpenAI.  
- **Adjust Quotas:** If you’re an admin, set per‑user request limits in `config.yaml` under `MAX_REQUESTS` and `RATE_LIMIT_INTERVAL`.

---

## 8. Getting Help  
- **GitHub Issues:** Report bugs or ask questions at https://github.com/byu-cpe/Maeser/issues.  


