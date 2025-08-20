# Setting Up a Discord Bot

Using the **maeser.discord_handler** package, you can create a **Discord bot** that interfaces with students on a Discord server with the same functionality. This guide provides instructions on setting up your own Maeser Discord bot.

---

## Prerequisites

- **The Maeser Package:** set up either in a development environment (see [**Development Setup Guide**](./development_setup.md)) or using `pip install maeser`.
- **One or More Chatbot Course Models:** created manually or using the [**Admin Portal**](./admin_portal.md) (recommended). If created manually, be sure to follow the [**Required Files and Directory Structure**](./handler_usage.md#required-files-and-directory-structure).

---

## Installing Additional Dependencies

The Discord handler requires extra dependencies that are not installed with Maeser by default. To install these dependencies, run:

```bash
pip install maeser[discord]
```

If you set up Maeser using the [**Development Setup Guide**](./development_setup.md), then you can skip this step (these dependencies were installed when `poetry install --all-extras` was run).

---

## Get Necessary Files From Maeser Repository

The Maeser GitHub repository contains the `example_handlers/` directory, which provides the following files:

- **`config_template.yaml`**: Configuration options used to set up the Discord handler with Maeser
- **`discord_example.py`**: A simple script demonstrating how to run Maeser's Discord handler.

If you have cloned the Maeser repository, simply navigate to this directory. Otherwise, copy these files to your project. To set up a Maeser Discord bot with these files, simply follow the instructions in this guide and run `discord_example.py` in the same directory as your `config.yaml` file.

---

## Set Up Config

If you have not already done so, make a copy of `config_template.yaml`, name it `config.yaml`, and update the following fields:

- **`openai_api_key`**: Place your OpenAI API key here.
- **`course_id`**: Populate this with the ID of the course that your Discord handler should use (see [**Creating and Modifying Courses**](#creating-and-modifying-courses)).
- **`vectorstore:vec_store_path`**: The Discord handler will look for course models in the directory declared by this field (see [**Creating and Modifying Courses**](#creating-and-modifying-courses)). By default, this directory is set to `bot_data/`, but you may update it with a different directory of your choice if desired.
- **`discord:intro`**: If desired, replace the default intro message with a custom message of your choice. This message will appear when you send your Discord bot the `!intro` command (see [**Administrator Commands**](#administrator-commands)).

In order to connect your Discord bot to the Maeser Discord handler, you need to have a Discord bot token. You will add your Discord bot token to the **`discord:discord_token`** file after you [**set up the Discord bot on the Discord website**](#set-up-the-discord-bot-on-the-discord-website).

> **Note:** The `config.yaml` located in `example_handlers/` is separate from the `config.yaml` used in `example/apps/`. Be careful not to confuse these two files when updating your config.

Future plans may include entering the token details in the [**Admin Portal**](./admin_portal.md), but for now, it must be entered manually.

---

## Creating and Modifying Courses

The Discord handler will look for the **course model** declared in `config.yaml`. **Course models** can be configured and modified using the [**Admin Portal**](./admin_portal.md). The course model you use with your Discord bot should be located in the directory defined by `vectorstore:vec_store_path` in `config.yaml`.

> **Note:** Your course must have a configured `bot.txt` file to be recognized by the Discord handler. For more information, see [**Required Files and Directory Structure**](./handler_usage.md#required-files-and-directory-structure) and [**bot.txt Syntax**](./handler_usage.md#bottxt-syntax) in the Handler Usage Guide.

---

## Set Up the Discord Bot on the Discord Website

Go to the [**Discord for Developers**](https://discord.com/developers/applications) website and set up an account if needed.

In the `Applications` tab, click `New Application`. Give it a name, and then click `Create`.

The following sections will cover each Menu item.

---

### General Information

The information here is optional, but may be helpful if managing multiple bots.

---

### Bot

You will want to define a bot **icon** and **username** here. This will be as if you are creating an account for the bot as a person (username and user icon).

Generate your **Discord bot token** by clicking the button labeled "Reset Token". **Copy this token to `config.yaml`** (in the `discord_token` field).

> **Note:** If you ever lose your bot token, you can generate a new token using "Reset Token". Be sure to update `config.yaml` as well.

After acquiring your bot token, scroll down to the `Privileged Gateway Intents` section and enable the following intents:

- Server Members Intent
- Message Content Intent

Be sure to **save your changes** before leaving this page.

---

### OAuth2

This is a key part of the setup process. Scroll down to "OAuth2 URL Generator" and select `bot`; a new menu labeled "Bot Permissions" will appear below the OAuth2 URL Generator. The following options (all under "Text Permissions") must be ticked enabled in order for the bot to run properly. **It will not work if these are not marked:**

- Send Messages
- Send Messages in Threads
- Send TTS Messages
- Manage Messages
- Embed Links
- Attach Files
- Read Message History
- Use Embedded Activities
- Use External Apps
- Create Polls

A URL will be generated at the bottom of this menu that allows your bot to be installed to Discord servers with the marked permissions. **Copy this URL** and enter it into your browser to add your bot to a Discord server. You may also share this URL with anyone who wishes to add your bot to their server.

---

## Run the Discord Handler

Once your bot is configured on the Discord website and `config.yaml` is configured, run `discord_example.py` within the directory of your `config.yaml` file. Your command output should look like the following:

```text
$ python dynamic_implementations/discord_handler.py
Using configuration at dynamic_implementations/config.yaml (Priority 0)
2025-07-30 10:29:44 INFO     discord.client logging in using static token
2025-07-30 10:29:44 INFO     discord.gateway Shard ID None has connected to Gateway (Session ID: <...>).
✅ Discord Bot connected as BotName#1984
```

---

## Set Up the Discord Bot on a Discord Server

After adding your Discord bot to a Discord server (see [**OAuth2**](#oauth2)), your server members can start conversing with your bot by sending it a direct message. The easiest way to present your bot to your server members is by adding it to its own channel on the server and sending an introduction message. To do this, follow the steps below:

1. **Create a new text channel** on your Discord server (e.g. "#chatbot").
2. **Edit the channel settings** by clicking the gear icon next to the channel name or by right clicking the channel and selecting "Edit Channel".
3. In **Permissions > Advanced Permissions**, make sure "@everyone" is selected in the "Roles/Members" menu, and **set "Send Messages" to disabled**.
4. In the "Roles/Members" menu, select your Discord bot (e.g. "BotName#1984"), and **set "Send Messages" to enabled**. Save and close out of Channel Settings.
5. In a new channel message, mention your Discord bot (e.g. type "@BotName" and select your bot from the dropdown list), type "!intro", and press enter. The chatbot should respond with a message similar to the following:
    > **👋 Hi there! I'm `@BotName`**  
    > I'm your digital assistant for this course!  
    > I have access to the course textbook and materials, so I can help you with explanations, examples, and guidance whenever you need it.  
    > **Let's get started!** Just send me a DM by clicking my name 👉 `@BotName` 👈

    You can change the introduction message by modifying the **`discord:intro`** field in your `config.yaml` file.

You now have a read-only channel on your Discord server that students can use to directly message your Discord bot.

---

## Administrator Commands

Administrator commands control the behavior of your chatbot in your Discord server. You can run a command by sending a message into the chat with the following format:

```{code-block} text
:class: no-copybutton
@BotName [COMMAND]
```

Replace "**BotName**" with a mention to your bot (e.g. type "@BotName" and select your bot from the dropdown list), and replace "**\[COMMAND\]**" with one of the following commands:

- **`!intro`**: Sends the default introduction message to the chat. You can change the introduction message by modifying the **`discord:intro`** field in your `config.yaml` file.
- **`!say [CONTENT]`**: Sends **\[CONTENT\]** into the chat. Be sure your message is surrounded by quotes (e.g. `!say "Hello World."`). Any additional arguments will be sent on a new line.

---

## Using the Discord Bot

To use your Discord Bot, simply send it a direct message after it has been set up.

- Ask it questions just like you would with any chatbot interface. It's status will update to "typing..." while it is generating a response.
- The Discord bot has some functionality for pulling figures from the course textbook/resources if figures are present in the course's vector store/dataset folders. Keep in mind, however, that the figure extraction script used by the [**Admin Portal**](./admin_portal.md) is currently very rudimentary and can use much improvement.
