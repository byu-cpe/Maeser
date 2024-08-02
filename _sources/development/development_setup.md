# Setting up the Development Environment

These are the instructions you would follow to do modifications to the Maeser package itself.

## Cloning the Repository

1. Open your terminal or command prompt.
2. Navigate to the directory where you want to clone the repository.
3. Run the following command to clone the repository:

   `git clone https://github.com/byu-cpe/Maeser`

## Create a Virtual Environment

It is highly recommended that you use a python virtual environment for your system. Instructions are given in the [User Setup Guide](user_setup.md) for doing so.

## Installing Dependencies

1. Change to the cloned directory:

`cd Maeser`

2. Install the project in editable mode using pip:

`pip install -e .`

This will install Maeser in a way that allows you to make changes to the source code and have them reflected immediately.

3. Install poetry itself if you haven't previously done so. If you are working in a virtual environment you can simply do:

`pip install poetry`

4. Then, install the project dependencies:

`poetry install`

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
