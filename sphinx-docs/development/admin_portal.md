# Using The Admin Portal for generating and modifying data

## Home Page

The admin portal currently only does two things:

- Create a New Course
- Modify a Course

Ideally, there will be more functions in the future, like being able to delete courses and launch different handlers (like discord) from the webapp.

## Creating a Course

A new course takes in three things:

- **Course ID**, such as "ECEN320"
- **PDF Files**
  - to add something like a textbook, click "**Add File Group**" to add a file group.
  - You may upload as many pdf files as you would like to the dialog window.
  - Make as many file groups as you want resources. The Universal_RAG takes the names of these file groups to figure out what to look through.
- **Rules**
  - These should be short sentences, dictating what you want the bot to do.
  - Click "**Add Rule**" to add a rule.

When you are done, click "**Submit Model**". The webpage will hold while the data is being processed. When the process is complete, it will return to the home page.

## Altering Courses

You may alter a course by clicking "**Manage Models**" -> Edit next to your desired course.

When a new form pops up, you may:

- Add and subtract rules from the rule list
- Delete existing datasets
- Add new File groups (datasets)

When everything is finished to your liking, click "**Update Model**" to confirm it. It should return you to the Manage Models page.

## Code Overview

The client is entirely self contained. This is intended to make it possible to run in its own docker container, protecting your model. It currently pulls keys from its own `config.py` which retrieves it from an external config.yaml.

To run the webserver, make sure you are running everything **Inside the web_client folder**. When you are in the folder, run `python flask_webserver.py`. This will run so long as the terminal session is live, making it easy to access, same as any flask app. It is set up on the default port "5000".

User login is only defined right now with one account, which should be changed later to be more dynamic. It can be found in this code snippet:

```python
USER = {
    'username': 'adam',
    'password': 'ajosiahs',
    'is_admin' : True
}
```

on line 17.

After you have set up rules and such, you will need to set up your handlers. There are various guides for setting up specific handlers:

- [Discord](discord.md)
