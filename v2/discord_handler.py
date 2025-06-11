import discord
import asyncio
import os
import re
from terminal_script import handle_message, get_valid_course_ids
from config import DISCORD_BOT_TOKEN
import maeser.graphs.universal_rag as RAG_VARS

# Setup intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True

client = discord.Client(intents=intents)

# Session tracking
discord_user_course_ids = {}
awaiting_course_id_users = set()

FIGURE_DIR = ""
RESOURCE = ""

# Helper: Extract figure references like "1_page3_fig2"
def extract_figures_from_text(text):
    # Finds "Figure 13.2" and extracts just "13.2"
    pattern = r'Figure (\d+\.\d+)'
    return re.findall(pattern, text)

def split_string(text, max_length=1999):
    chunks = []
    while len(text) > max_length:
        # Try to split at the last newline before max_length
        split_index = text.rfind('\n', 0, max_length)
        if split_index == -1:
            # Try to split at the last space before max_length
            split_index = text.rfind(' ', 0, max_length)
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
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    msg_text = message.content.strip()

    # -- START SESSION HANDLER --
    if msg_text.lower().startswith("!start"):
        if user_id in awaiting_course_id_users:
            await message.channel.send("You are already starting a session. Please provide your course ID or wait for timeout.")
            return

        await message.channel.send("🧑‍🏫 Please enter your course ID:")
        awaiting_course_id_users.add(user_id)

        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.strip()

        try:
            reply_message = await client.wait_for("message", check=check, timeout=60)
            course_id = reply_message.content.strip()
            valid_courses = get_valid_course_ids()

            if course_id not in valid_courses:
                await message.channel.send(f"❌ Invalid course ID. Available options: {', '.join(valid_courses)}")
                return

            discord_user_course_ids[user_id] = course_id
            await message.channel.send(f"✅ Session started for course `{course_id}`! Send your question.")

        except asyncio.TimeoutError:
            await message.channel.send("⏱️ Timeout: You didn’t reply in time. Try `!start` again.")
        except Exception as e:
            await message.channel.send(f"❌ Error starting session: {e}")
        finally:
            awaiting_course_id_users.discard(user_id)
        return

    # Ignore input while waiting for course ID
    if user_id in awaiting_course_id_users:
        return

    # -- MESSAGE PROCESSING --
    if user_id in discord_user_course_ids:
        course_id = discord_user_course_ids[user_id]
        try:
            reply = handle_message(user_id, course_id, msg_text)
            # Send text reply
            if(len(reply)>1999):
                chunks = split_string(reply)
                for i in chunks:
                    await message.channel.send(f"🤖 {i}")
            else:   
                await message.channel.send(f"🤖 {reply}")

            try:
                # Extract and send figures if referenced

                FIGURE_DIR = f"v2/bot_data/{course_id}/{RAG_VARS.recommended_topics[0]}"
                figure_names = extract_figures_from_text(reply)
                files = []
                for fig in figure_names:
                    image_path = os.path.join(FIGURE_DIR, f"{fig}.png")
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
    else:
        await message.channel.send("❗ Please start a session first using `!start`.")

# Run the bot
client.run(DISCORD_BOT_TOKEN)
