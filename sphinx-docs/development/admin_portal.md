# The Admin Portal: Generating and Modifying Course Models

Recall that in order to give the Maeser chatbot resources to pull from, the resources must be converted to an LLM-friendly format called a **vector store**. Writing Python scripts to [**embed new content**](./embedding.md) in this way can be cumbersome. To simplify the process of creating new vector stores and course models, the **Admin Portal** vectorizes content and controls chatbot behavior via a simple web client.

The admin portal currently has the following functionality:

- **Create a New Course**
- **Manage Courses**
- **Modify a Course**
- **Delete a Course**

The admin portal is relatively new and is still a work in progress; ideally, there will be more functions in the future, like being able launch different handlers (such as [**Discord**](./discord.md)).

---

## Creating a Course

A **course model** (or simply "course") takes in a **course ID**, **PDF Datasets**, and **Rules**. The following sections outline these fields in more detail and explain how to add these to your course via the "**Design New Model**" or "**Edit Model**" web views in the admin portal.

### Course ID

The course ID will be used by students to select your course when interacting with the chatbot. This identifier should be short and descriptive, like "ECEN320".

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

The "**Managing Courses**" page lists all course models in your bot store path. Here you can either **edit** or **delete** courses. The process for editing a course is the same as [**creating a new course**](#creating-a-course).

---

## Code Overview

The admin portal is entirely self contained. This is intended to make it possible to run it in its own docker container, protecting your model. It currently pulls keys from its own `config.py` which retrieves it from an external `config.yaml`.

Unlike the other scripts in the Maeser repository, **you need to be inside the admin_portal folder (not the project root) to run the web server**. When you are in this folder, simply run:

```bash
python flask_admin_portal.py
```

This will start up the admin portal web server (on port 5000 and in debug mode, by default).

User login is only defined right now with one account, which should be changed later to be more dynamic. It can be found in the `USER` parameter within `flask_admin_portal.py`:

```python
USER = {
    'username': 'adam',
    'password': 'ajosiahs',
    'is_admin' : True
}
```

After you have set up rules and such, you will need to set up your handlers, found in [**`dynamic_implementations/`**](./handler_usage.md#dynamic-implementations-of-generate_responsepy). Currently, this directory only has handlers for a simple web server and for Discord.

Follow the guide at [**Setting Up a Discord Bot**](discord.md) to integrate your chatbot with Discord.
