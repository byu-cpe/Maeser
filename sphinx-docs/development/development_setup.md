# Setting up the Development Environment

## Prerequisites
- Git
- Python (version 3.10 or later)
- Poetry (Python dependency management tool)

## Cloning the Repository
1. Open your terminal or command prompt.
2. Navigate to the directory where you want to clone the repository.
3. Run the following command to clone the repository:
git clone https://github.com/username/maeser.git


Replace `https://github.com/username/maeser.git` with the actual URL of the repository.

## Installing Dependencies

### If you're developing Maeser itself
1. Change to the cloned directory:
cd maeser


2. Install the project in editable mode using pip:
pip install -e .


This will install Maeser in a way that allows you to make changes to the source code and have them reflected immediately.

### If you're creating an application that uses Maeser
1. Change to the cloned directory:
cd maeser


2. Install the project dependencies using Poetry:
poetry install


3. Install the Maeser package from the `dist` directory:

pip install dist/maeser*.tar.gz


This will install the latest version of Maeser from the local distribution package.

## Running Tests
After installing the dependencies, you can run the test suite to ensure everything is working correctly:

pytest tests/


## Building Documentation
If you're working on the project documentation, you can build it locally using Sphinx:

cd docs/
make html


This will generate the HTML documentation in the `docs/_build/html` directory.

## Additional Steps
- Set up any required environment variables or configuration files.
- Refer to the project's README or contributing guidelines for more information on development workflows, coding standards, and other relevant details.