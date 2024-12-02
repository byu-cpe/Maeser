# Development Setup with Windows Subsystem Linux

## Cloning the Repository

Follow the [development setup instructions](./development_setup.md) for how to clone the repository onto your computer. Using WSL may help you install the package with poetry and pip.

## Setting Up WSL on Windows

1) Install WSL, change the default Linux distribution, and set up user info with [this tutorial](https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command) from Microsoft.
    - You may get the following error during installation.
        ```
        Installing, this may take a few minutes...
        WslRegisterDistribution failed with error: 0x800701bc
        Error: 0x800701bc WSL 2 ?????????????????? https://aka.ms/wsl2kernel
        ```
      If so, download and install the [Linux kernel update package](https://learn.microsoft.com/en-us/windows/wsl/install-manual#step-4---download-the-linux-kernel-update-package), and try again.
2) Run the following commands: (this assumes you are using the Ubuntu distribution)
    - `sudo apt-get update`
    - `sudo apt-get upgrade`
    - `sudo apt-get install python3-pip`
3) Open the command line and navigate to the directory where you've cloned the repository. If the repository is located somewhere in your Windows filesystem, you'll need to prefix the filepath with `/mnt/`. This is because WSL (Windows Subsystem for Linux) mounts your Windows filesystem under the `/mnt/` directory. So, to change the directory to your repository, the command would be in the format: `cd /mnt/<Windows filepath to your repository>`.

## Development

Follow the [development setup instructions](./development_setup.md) for how to use the make file to configure and run the application and how to run the application without it.