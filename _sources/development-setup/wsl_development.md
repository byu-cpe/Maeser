# Development Setup with WSL (Windows Subsystem for Linux)

This guide details how to leverage **Windows Subsystem for Linux (WSL 2)** to create a robust Maeser development environment on a Windows machine. By following these steps, you’ll install and configure WSL, set up your Linux distribution (Ubuntu), install essential development tools, and run Maeser seamlessly within WSL.

---

## Introduction to WSL

The **Windows Subsystem for Linux (WSL)** is a compatibility layer that allows you to run a GNU/Linux environment natively on Windows without the overhead of a virtual machine or dual-boot setup. WSL 2 uses a real Linux kernel via a lightweight VM, offering near-native performance and full system-call compatibility ([en.wikipedia.org](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux)).

**Why use WSL for Maeser development?**

- **Unified Environment**: Use Linux-based tooling (bash, Python, make) directly on Windows.  
- **Performance**: WSL 2 delivers faster file system I/O and process performance compared to WSL 1 ([learn.microsoft.com](https://learn.microsoft.com/cs-cz/windows/wsl/install-on-server)).  
- **Consistency**: Mirror Linux production setups, reducing “works on my machine” issues.  
- **Integration**: Access Windows files from Linux and vice versa, and use VS Code’s Remote - WSL extension for a seamless IDE experience.

---

## Install & Enable WSL

1. **Open PowerShell as Administrator**.  
2. Run the following command to install WSL 2 and the default Ubuntu distribution:
   ```powershell
   wsl --install
   ```
   This single command enables required features, downloads the Linux kernel, sets WSL 2 as default, and installs Ubuntu ([learn.microsoft.com](https://learn.microsoft.com/en-us/windows/wsl/install)).
3. **Restart** your machine when prompted.
4. On reboot, **complete the Ubuntu setup** by creating your Linux user account and password.

> **Tip:** To install a specific distribution (e.g., Debian), use:
> ```powershell
> wsl --install -d Debian
> ```

---

## Update & Upgrade Your Linux Distro

1. Open **Ubuntu (WSL)** from the Start menu.  
2. Update package lists and upgrade installed packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. Install essential build tools:
   ```bash
   sudo apt install -y build-essential git curl python3.10 python3.10-venv python3-pip make
   ```

---

## Configure WSL Settings (Optional)

Create a **`.wslconfig`** file in your Windows user directory (e.g., `C:\Users\You`) to customize WSL 2 VM resources:

```ini
[wsl2]
memory=4GB   # Limits VM to 4 GB RAM
#processors=2 # Uncomment to limit to 2 CPU cores
swap=0       # Disable swap (optional)
```

This file is automatically applied on WSL restarts ([en.wikipedia.org](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux)).

---

## Clone & Set Up Maeser in WSL

1. **Navigate** to your development folder, for example:
   ```bash
   cd ~
   mkdir projects && cd projects
   ```
2. **Clone** the Maeser repository:
   ```bash
   git clone https://github.com/byu-cpe/Maeser.git
   cd Maeser
   ```
3. **Create** a Python virtual environment and activate it:
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```
4. **Install** Maeser and development dependencies:
   ```bash
   make setup
   ```

> `make setup` runs `pip install -e .`, installs Sphinx, pytest, and other requirements, and executes the test suite.

---

## Build & Preview Documentation

Within your activated environment:

```bash
cd sphinx-docs
make html
```

To view the documentation, look for the file named `index.html` in the `_build\html\` directory, and open the file in your Windows browser. If you have the `wslu` library installed, you can do this directly from the WSL terminal:
```bash
wslview _build/html/index.html
```

---

## Using VS Code with WSL

1. Install the **[Remote - WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl)** extension in VS Code.  
2. Open your Maeser folder in WSL by clicking **Remote Explorer → WSL Targets → Ubuntu** and selecting your project.  
3. VS Code now uses the Linux toolchain inside WSL for linting, debugging, and terminal commands.

---

## Accessing Windows Files

- Windows drives are mounted under `/mnt`, e.g., your `C:` drive at `/mnt/c`.  
- To edit files on Windows from WSL, navigate to `/mnt/c/path/to/file` and open them with Linux editors or VS Code.

---

## Additional Resources

- **Microsoft’s WSL Install Guide**: Detailed walkthrough for various Windows versions ([learn.microsoft.com](https://learn.microsoft.com/en-us/windows/wsl/install)).  
- **WSL Overview & Tutorials**: In-depth docs on WSL features and GUI support ([learn.microsoft.com](https://learn.microsoft.com/en-us/windows/wsl/)).  
- **WSL FAQ**: Answers to common questions about WSL usage ([learn.microsoft.com](https://learn.microsoft.com/en-us/windows/wsl/faq)).


