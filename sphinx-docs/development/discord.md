# Setting up a Discord Bot

## Setting up Config.yaml

In order for Discord to talk with your script, you need to have a discord bot token. This token will go under the section in your `config.yaml` in the `dynamic_implementations` folder.


Future plans may include entering the token details in the administrator app, but for now, it must be entered manually.

## Setting Up the Discord bot on the Discord Website
Go to the [Discord for Developers](https://discord.com/developers/applications) website, and set up an account if needed.

In the `Applications` tab, click `New Application`. Give it a name, and then click `Create`.

The following sections will cover each Menu item.

### General Information ###
The information here is optional, but may be helpful if managing multiple bots.

### OAuth2 ###
In the OAuth2 → URL Generator:

Under Scopes, check:
- dm_channels.messages.read
- messages.read
- dm_channels.read
- presences.write
- dm_channels.messages.write 
- bot
- gateway.coonnect

A URL will be generated at the bottom — copy and open it in your browser.

Select a server you own or have permission to add bots to. If you need to do this, go and set one up, and then come back to this step.

Click `Authorize`.


### Bot ###
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

### Installation ###

When you are finished with your permissions and such, you may share the link under the `Install Link` with individuals you want to share this with.

## Using Discord ##
To use the discord app, you may begin a DM with the bot after it has been set up.
- `!start` to begin a new conversation at any time, in any course
- `!end` to end a conversation
- Type in a course code from any set up courses. If the course you type is unavailable, it will give you a list of courses. As of right now, you must retype `!start` if the course is unavailable to begin a conversation with an available course.
