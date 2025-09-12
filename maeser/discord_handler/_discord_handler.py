# SPDX-License-Identifier: LGPL-3.0-or-later

import discord
import os
import re
from maeser.generate_response import handle_message, get_valid_course_ids, BOT_DATA_PATH
from maeser.config import COURSE_ID, DISCORD_BOT_TOKEN, DISCORD_INTRO
import shlex

import maeser.graphs.universal_rag as RAG_VARS

# Setup intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True

client = discord.Client(intents=intents)


# Helper: Extract figure references like "1_page3_fig2"
def extract_figures_from_text(text: str) -> list[str]:
    """Finds all references to figures in **text** and returns a list of figure IDs.

    The reference to the figure should be formated like "Figure X.X".
    Only "X.X" (the figure ID) will be extracted and added to the resulting list.

    Args:
        text (str): The text containing figure references.

    Returns:
        list[str]: A list of figure IDs.
    """
    # Finds "Figure 13.2" and extracts just "13.2"
    pattern = r"Figure (\d+\.\d+)"
    return re.findall(pattern, text)


def split_string(text: str, max_length=1999) -> list[str]:
    """Splits one strings into multiple strings so that all resultant chunks are shorter
    than **max_length**.

    Checks for a semantically clean place to split the text first (e.g. at a whitespace).
    If a clean place to split is not found, force-splits at **max_length**.

    Args:
        text (str): The text to split.
        max_length (int, optional): The maximum length any chunk can be after splitting. Defaults to 1999.

    Returns:
        list[str]: The list of text chunks that make up the original **text**.
    """
    chunks = []
    while len(text) > max_length:
        # Try to split at the last newline before max_length
        split_index = text.rfind("\n", 0, max_length)
        if split_index == -1:
            # Try to split at the last space before max_length
            split_index = text.rfind(" ", 0, max_length)
        if split_index == -1:
            # No good split point; force split
            split_index = max_length

        chunks.append(text[:split_index].strip())
        text = text[split_index:].strip()

    if text:
        chunks.append(text)

    return chunks


def is_admin_message(message: discord.Message) -> bool:
    """Checks to see if a message was sent by a channel administrator.

    Args:
        message (discord.Message): The message to check administrator privileges for.

    Returns:
        bool: True if the message sender is an administrator for the channel the message was sent in.
    """
    return (
        message.guild is not None
        and message.channel.permissions_for(message.author).administrator
    )


async def command_say(
    channel: discord.abc.Messageable,
    content: str,
) -> None:
    """Say **content** in **channel**.

    Args:
        channel (discord.abc.Messageable): The channel to send the message in.
        content (str): The content of the message.
    """
    await channel.send(content)


async def command_intro(channel: discord.abc.Messageable) -> None:
    """Sends the default intro message into **channel**.

    This message can be configured in the "discord:intro" field in `config.yaml`.
    All instances of "@self" in the text will be replaced with a mention to the
    Discord bot (e.g. "@BotName").

    Args:
        channel (discord.abc.Messageable): The channel to send the intro message in.
    """
    intro_content: str = DISCORD_INTRO.replace("@self", client.user.mention)
    await channel.send(intro_content)


async def run_admin_command(message: discord.Message, command_args: list[str]) -> None:
    channel = message.channel
    argc: int = len(command_args)
    match command_args[0]:
        case "!say":
            if argc < 2:
                await channel.send(
                    "Usage: `!say [CONTENT]`\n"
                    'Use quotes around CONTENT (e.g. `!say "Hello World!"`)\n'
                    "Additional arguments will be sent on a new line."
                )
                return
            say_text: str = "\n".join(command_args[1:])
            await command_say(channel, say_text)
            await message.delete()

        case "!intro":
            await command_intro(channel)
            await message.delete()


@client.event
async def on_ready():
    print(f"✅ Discord Bot connected as {client.user}")


@client.event
async def on_message(message: discord.Message):
    # Get data from message
    user_id = str(message.author.id)
    msg_text = message.content.strip()
    channel = message.channel

    # Ignore if message is from bot or if message is blank
    if message.author.bot or len(msg_text) == 0:
        return

    # Only run admin commands if message is not a DM
    if not isinstance(channel, discord.DMChannel):
        if is_admin_message(message):
            msg_args = shlex.split(
                msg_text
            )  # Gets list of args as if msg_text was a terminal command

            # Bot must be mentioned first
            # and message must contain a command (not just a bot mention)
            if msg_args[0] == client.user.mention and len(msg_args) > 1:
                command_args = msg_args[1:]  # remove chatbot mention
                await run_admin_command(message, command_args)
        return

    # -- MESSAGE PROCESSING --
    async with channel.typing():
        try:
            reply = handle_message(user_id, COURSE_ID, msg_text)
            # Send text reply
            if len(reply) > 1999:
                chunks = split_string(reply)
                for chunk in chunks:
                    await channel.send(chunk)
            else:
                await channel.send(reply)

            try:
                # Extract and send figures if referenced

                figure_dir = (
                    f"{BOT_DATA_PATH}/{COURSE_ID}/{RAG_VARS.recommended_topics[0]}"
                )
                figure_names = extract_figures_from_text(reply)
                files = []
                for fig in figure_names:
                    image_path = os.path.join(figure_dir, f"{fig}.png")
                    if os.path.exists(image_path):
                        files.append(discord.File(image_path, filename=f"{fig}.png"))
                    else:
                        print(f"[WARN] Figure not found: {image_path}")

                if files:
                    await channel.send(files=files)
            except Exception:
                print("❌ There was an issue sending figures.")

        except Exception as e:
            await channel.send(f"❌ Error: {e}")


def run_discord_handler(course_id: str = COURSE_ID, bot_token: str = DISCORD_BOT_TOKEN) -> None:
    """Runs the discord handler by setting up a RAG Graph with **course_id** and connecting
    it to a discord bot with **bot_token**.

    Args:
        course_id (str, optional): The course ID the RAG Graph should use for context. Defaults to maeser.config.COURSE_ID.
        bot_token (str, optional): _description_. Defaults to maeser.config.DISCORD_BOT_TOKEN.
    """
    if course_id not in get_valid_course_ids():
        print(f"ERROR: Course ID {course_id} not a valid course ID.")
        exit(1)

    client.run(bot_token)


if __name__ == "__main__":
    run_discord_handler(COURSE_ID, DISCORD_BOT_TOKEN)
