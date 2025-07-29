# Setting up a Discord Bot

<!-- TODO: Add an overview here -->

## Setting up Config.yaml

In order for Discord to talk with your script, you need to have a discord bot token. This token will go under the section in your `config.yaml` in the `dynamic_implementations/` folder. If you have not already done so, make a copy of `dynamic_implementations/config_template.yaml`, name it `config.yaml`, and populate it with your OpenAI API key and Discord token.

> **Note:** The `config.yaml` located in `dynamic_implementations/` is completely separate from the `config.yaml` used in `example/`. Be careful not to confuse these two files when updating your config.

Future plans may include entering the token details in the [**Admin Portal**](./admin_portal.md), but for now, it must be entered manually.

## Setting Up the Discord bot on the Discord Website

Go to the [**Discord for Developers**](https://discord.com/developers/applications) website, and set up an account if needed.

In the `Applications` tab, click `New Application`. Give it a name, and then click `Create`.

The following sections will cover each Menu item.

### General Information

The information here is optional, but may be helpful if managing multiple bots.

### Bot

You will want to define a bot icon and username here. This will be as if you are creating an account for the bot as a person (username and user icon).

If you were unable to obtain a token earlier, you can always reset the token with the `Reset Token` button on this page.

You will also want to scroll down to the `Privileged Gateway Intents` section.

The following must be ticked `enabled` in order for the bot to run properly. **It will not work if these are not marked.**

- Server Members Intent
- Message Content Intent
- Send Messages
- Send Messages in Threads
- Send TTS Messages
- Embed Links
- Attach Files
- Read Message History
- Use Embedded Activities
- Use External Apps
- Create Polls

### OAuth2

This is a key part of the setup process. Scroll down to OAuth2 URL Generator, select `bot`. If permissions have not been added yet, you can add them here.

Copy the generated url and enter it into your browser to set it up.

### Installation

When you are finished with your permissions and such, you may copy and paste the install link into your browser window, which should allow you to interact with the bot. After setting it up, you are more than welcome to share it with others if you'd like.

## Using Discord

To use the discord app, you may message the bot within a server or directly message it after it has been set up.

- `!start` to begin a new conversation at any time, in any course.
- `!end` to end a conversation.
- Type in a course code from any set up courses. If the course you type is unavailable, it will give you a list of courses and prompt you for a course ID again.
