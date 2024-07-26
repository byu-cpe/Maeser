# Setting up the Development Environment

## Prerequisites

- Git
- Python (version 3.10 or later)
- Poetry (Python dependency management tool)

## Cloning the Repository

1. Open your terminal or command prompt.
2. Navigate to the directory where you want to clone the repository.
3. Run the following command to clone the repository:

   `git clone https://github.com/byu-cpe/Maeser`

## Create a Virtual Environment

It is highly recommended that you use a python virtual environment for your system so that (1) you don't have to install packages system-wide (which you may not have privileges to do) and (2) so that you have total control over the installed software versions. There are two main virtual environment approaches, each with their own adherents and each with its own operational methods.

### Virtual Environments: Conda

1. You can install Conda using:

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
```

Note that for Mac OS X, replacing Linux with MacOSX will do the trick.

2. Next, you can make a new virtual environment with any specific version of python with the following:

`conda create --name maeserEnv python=3.10 pip`

3. Finally, you activate the virtual environment with:

`conda activate maeserEnv`

and you deactivate it with:

`conda deactivate`

### Virtual Environments: venv

1. You create a new venv with the following. Make sure you are in the Maeser directory when you do it. Also, note that the version of python that will be installed into the venv will be whatever python you run to create the venv. As a result, you may first have to install a specific python on your machine to get what you want.

`python3 -m venv .`

2. Next, you activate the virtual environment with:

`source ./bin/activate`

and you deactivate it with:

`deactivate`

## Installing Dependencies

### If you're developing Maeser itself

1. Change to the cloned directory:

`cd Maeser`

2. Install the project in editable mode using pip:

`pip install -e .`

This will install Maeser in a way that allows you to make changes to the source code and have them reflected immediately.

### If you're creating an application that uses Maeser

1. Change to the cloned directory:

`cd Maeser`

2. Install poetry itself if you haven't previously done so.  If you are working in a virtual environment you can simply do:

`pip install poetry`

If you are not using a virtual environment then you will have to install it system-wide using a package manager such as:

`sudo apt install python3-poetry`

3. Then, install the project dependencies:

`poetry install`

4. Install the Maeser package from the `dist` directory: **This doesn't work.**

`pip install dist/maeser\*.tar.gz`

This will install the latest version of Maeser from the local distribution package.

## Running Tests

After installing the dependencies, you can run the test suite to ensure everything is working correctly:

`pytest tests`

## Building Documentation

If you're working on the project documentation, you can build it locally using Sphinx:

`cd sphinx-docs`

`make html`

This will generate the HTML documentation in the `sphinx-docs/_build/html` directory.

## Additional Steps

- Set up any required environment variables or configuration files.
- Refer to the project's README or contributing guidelines for more information on development workflows, coding standards, and other relevant details.
