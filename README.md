# Maeser
## Overview
This package is designed to facilitate the creation of Retrieval-Augmented Generation (RAG) chatbot applications, specifically tailored for educational purposes. It leverages the capabilities of [LangGraph](https://langchain-ai.github.io/langgraph/), a powerful tool for serving RAG pipelines, to provide a robust backend for chatbot interactions.

Detailed documentation can be found [here](https://byu-cpe.github.io/Maeser/).
## Features
- **RAG Pipeline Integration**: Utilizes LangGraph to seamlessly integrate RAG pipelines into the chatbot, enhancing its ability to generate informative and contextually relevant responses.
- **Session Management**: Comes equipped with a session manager to handle interactions efficiently, ensuring a smooth and coherent conversation flow.
- **Web Interface**: Includes optional prebuilt Flask applications, making it easy to deploy the chatbot on a web browser for accessible and interactive user experiences.
- **Terminal Interface**: Offers a simple terminal interface for users who prefer a more straightforward method of interaction, making it versatile for different use cases.
## Potential Use Cases
* Help students study for an exam
  * Generate example problems
* Provide guided help for students completing homework
  * Not giving them the answers but providing hints and guided help to step them through the problems
  * Pointing the students back to the textbook or slides when guiding them
* Assist them in completing the labs
  * Review their code and provide feedback
  * Help them resolve common issues such as issues with the Vivado tools

## Getting Started
### Development Setup
To begin using the Maeser Chatbot, follow the [development setup instructions](https://byu-cpe.github.io/Maeser/development/development_setup.html).
This page includes instructions for cloning the repository and running the app.

> **NOTE:** This application is intended to run on Unix-based systems. For help running Maeser on Windows, follow the [development setup using Windows Subsystem Linux instructions](https://byu-cpe.github.io/Maeser/development/wsl_development.html).
### Example
For a fully working example application, follow the documentation for the [example application](https://byu-cpe.github.io/Maeser/development/flask_example.html).
### Embedding Context
Follow the documentation for embedding custom content [here](https://byu-cpe.github.io/Maeser/development/embedding.html).
### Graphs
An understanding of langchain and langgraph is necessary for customizing the application for any use case. Follow documentation and tutorials [here](https://langchain-ai.github.io/langgraph/).

## Repository Organization
### Directories:
- `maeser` contains the source code for the application.
- `dist` contains configuration and code for distributing the module.
- `requirements` contains python requirements files.
- `sphinx_docs` contains sphinx related code and various documentation files.
- `tests` contains unit test files for the application's source code. 

This package is licensed on the LGPL version 3 or later.
See [COPYING.LESSER.md](COPYING.LESSER.md) and [COPYING.md](COPYING.md) for details.

Other resources may be licensed under different compatible licenses, such as the [MIT License](https://opensource.org/license/mit) (Bootstrap Icons), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/legalcode) (normalize.css), or [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en) (images and vector stores).
