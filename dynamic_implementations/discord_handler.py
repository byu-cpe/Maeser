# SPDX-License-Identifier: LGPL-3.0-or-later

import discord
import os
import re
from generate_response import handle_message, get_valid_course_ids, BOT_DATA_PATH
from config import DISCORD_BOT_TOKEN, COURSE_ID

import maeser.graphs.universal_rag as RAG_VARS

# Setup intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True

client = discord.Client(intents=intents)


# Helper: Extract figure references like "1_page3_fig2"
def extract_figures_from_text(text):
    # Finds "Figure 13.2" and extracts just "13.2"
    pattern = r"Figure (\d+\.\d+)"
    return re.findall(pattern, text)


def split_string(text: str, max_length=1999):
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


@client.event
async def on_ready():
    print(f"✅ Discord Bot connected as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot or not isinstance(message.channel, discord.DMChannel):
        return

    user_id = str(message.author.id)
    msg_text = message.content.strip()

    # -- MESSAGE PROCESSING --
    async with message.channel.typing():
        try:
            reply = handle_message(user_id, COURSE_ID, msg_text)
            # Send text reply
            if len(reply) > 1999:
                chunks = split_string(reply)
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(reply)

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
                    await message.channel.send(files=files)
            except Exception:
                print("❌ There was an issue sending figures.")

        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")


if __name__ == "__main__":
    if COURSE_ID not in get_valid_course_ids():
        print(f"ERROR: Course ID {COURSE_ID} not a valid course ID.")
        exit(1)

    client.run(DISCORD_BOT_TOKEN)
