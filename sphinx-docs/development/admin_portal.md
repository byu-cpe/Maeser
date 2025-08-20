# The Admin Portal: Generate and Modify Course Models

In order to give the Maeser chatbot resources to pull from, the resources must be converted to an LLM-friendly format called a **vector store**. Writing Python scripts to [**embed new content**](./embedding.md) in this way can be cumbersome. To simplify the process of creating new vector stores and course models, the **maeser.admin_portal** package provides the **Admin Portal**, which vectorizes content and controls chatbot behavior via a simple web client.

The Admin Portal currently has the following functionalities:

- **Design a New Course**
- **Manage Courses**
- **Modify a Course**
- **Delete a Course**

The Admin Portal is relatively new and is still a work in progress; ideally, there will be more functions in the future, like being able launch different handlers (such as [**Discord**](./discord.md)).

---

## Prerequisites

- **The Maeser Package:** set up either in a development environment (see [**Development Setup Guide**](./development_setup.md)) or using `pip install maeser`.

---

## Installing Additional Dependencies

The Admin Portal requires extra dependencies that are not installed with Maeser. To install these dependencies, run:

```bash
pip install maeser[admin_portal]
```

If you set up Maeser using the [**Development Setup Guide**](./development_setup.md), then you can skip this step (these dependencies were installed when `poetry install --all-extras` was run).

---

## Get Necessary Files From Maeser Repository

The Maeser GitHub repository contains the `admin_portal/` directory, which provides the following files:

- **`config_template.yaml`**: Configuration options used to set up the Admin Portal.
- **`admin_portal_example.py`**: A simple script demonstrating how to configure and run Maeser's Admin Portal.

If you have cloned the Maeser repository, simply navigate to this directory. Otherwise, copy these files to your project.

---

## Set Up Config

If you have not already done so, make a copy of `config_template.yaml`, name it `config.yaml`, and update the following fields:

- **`api_keys:openai_api_key`**: Place your OpenAI API key here.
- **`vectorstore:vec_store_path`**: The Admin Portal will look for course models in the directory declared by this field. Update this field to a directory of your choice. If you are running the Admin Portal [**in the Maeser development environment**](./development_setup.md), then this field can be left as-is.

> **Note:** The `config.yaml` located in `admin_portal/` is separate from the `config.yaml` files used in `example/apps/` and in `example_handlers/`. Be careful not to confuse these files when updating your config.

---

## Set Up Username, Password, and Secret Key

To configure a username and password to be used with the Admin Portal, open `admin_portal_example.py` and locate the `USERNAME` and `PASSWORD` parameters near the top of the script. by default, these are set to "karl" and "karlgmaeser1", respectively. Replace these with a username and password of your choice.

You can also optionally define a secret key in the `SECRET_KEY` parameter. This is only necessary if you plan to the Admin Portal to production. For local use, you may leave this parameter as-is.

---

## Run the Admin Portal

After getting the necessary files from the Maeser repository and setting up all config and parameters as described above, simply run `admin_portal_example.py` in the same directory as your `config.yaml` file to start the Admin Portal web applet. You will see a command output similar to the following:

```bash
$ python admin_portal_example.py 
Using configuration at config.yaml (Priority 0)
 * Serving Flask app 'maeser.admin_portal._flask_admin_portal'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Click on the URL the applet is running on (e.g. `http://127.0.0.1:5000`) to open the Admin Portal in your web browser.

---

## Design a Course

A **course model** (or simply "course") takes in a **course ID**, **PDF Datasets**, and **Rules**. The following sections outline these fields in more detail and explain how to add these to your course via the "**Design New Model**" or "**Edit Model**" web views in the Admin Portal.

### Course ID

The course ID will be used by students to select your course when interacting with the chatbot. This identifier should be short and descriptive, like "CS101".

### PDF Datasets

A **dataset** is a set of PDFs that will be processed into a single vector store. It is best practice to make one dataset per type of resource (e.g. one dataset for your textbook, another dataset for your homework files, another dataset for your labs, etc.). The handlers in `dynamic_implementations/` will use the names of the datasets to identify the most relevant resources to pull from when interacting with a student.

To add a dataset, click "**Add Dataset**." You may add as many PDF files from a dataset as you would like using the dialog window, and you may add as many datasets as you would like using the "**Add Dataset**" button.

### Rules

The **rules** are the set of instructions that the chatbot will try to follow when interacting with students. These should be short sentences, dictating what you want the bot to do.

To add a rule, click "**Add Rule**." If you are unsure what rules to give your chatbot, here is a good starting point:

- `You are a helpful professor of <name_of_course>.`
- `You will answer student's questions about the course based on the context provided.`
- `If the question is unrelated to the topic or the context, politely inform the user that their question is outside the context of your resources.`

### Submit Model

When you are done, click "Submit Model" (in "**Design New Model**") or "Update Model" (in "**Edit Model**"). The webpage will hold while the data is being processed, and progress will be printed to the terminal. If the process completes successfully, the model will be saved to your bot store path (`dynamic_implementations/bot_data` by default) and you will be redirected to the "**Manage Models**" page.

---

## Managing Courses

The "**Managing Courses**" page lists all course models in your bot store path. Here you can either **edit** or **delete** courses. The process for editing a course is the same as [**creating a new course**](#design-a-course).

---

## Next Steps

- **Set Up Handlers:** After you have set up rules and such, you will need to set up your handlers, found in [**`example_handlers/`**](./handler_usage.md#dynamic-implementations-of-generate_responsepy). Currently, this directory only has a handler for Discord. Follow the guide at [**Setting Up a Discord Bot**](discord.md) to integrate your chatbot with Discord.
