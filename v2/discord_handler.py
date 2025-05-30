import discord
import asyncio
from terminal_script import handle_message, get_valid_course_ids # Import necessary functions from terminal_script
from config import DISCORD_BOT_TOKEN

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True  # IMPORTANT for DM support

client = discord.Client(intents=intents)

# Track user sessions for COURSE_ID selection: {user_id: course_id}
# This maps a Discord user ID to the course ID they've selected.
# The actual Maeser conversation state is managed by handle_message using user_id:course_id.
discord_user_course_ids = {}

# NEW: A set to track users who are currently expected to submit a course ID
awaiting_course_id_users = set()

@client.event
async def on_ready():
    print(f"✅ Discord Bot connected as {client.user}")

@client.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return

    user_id = str(message.author.id)
    msg_text = message.content.strip()

    # --- Step 1: Handle '!start' command ---
    if msg_text.lower().startswith("!start"):
        # If the user is already in the process of starting a session, inform them
        if user_id in awaiting_course_id_users:
            await message.channel.send("You are already in the process of starting a session. Please provide your course ID or wait for timeout.")
            return

        await message.channel.send("🧑‍🏫 Please enter your course ID:")
        awaiting_course_id_users.add(user_id) # Mark user as awaiting course ID

        def check(m):
            # Check if the reply is from the same author and channel
            # and is not empty
            return m.author == message.author and m.channel == message.channel and m.content.strip()

        try:
            # Wait for the user's reply containing the course ID
            reply_message = await client.wait_for("message", check=check, timeout=60)
            course_id = reply_message.content.strip()

            valid_courses = get_valid_course_ids() # Use the helper from terminal_script
            if course_id not in valid_courses:
                await message.channel.send(f"❌ Invalid course ID. Available options: {', '.join(valid_courses)}")
                return

            discord_user_course_ids[user_id] = course_id # Store the chosen course_id
            await message.channel.send(f"✅ Session started for course `{course_id}`! Send your question.")
            
        except asyncio.TimeoutError:
            await message.channel.send("⏱️ Timeout: You didn’t reply in time. Try `!start` again.")
        except Exception as e:
            await message.channel.send(f"❌ Error starting session: {e}")
        finally:
            # Ensure the user is removed from the awaiting set regardless of success or failure
            awaiting_course_id_users.discard(user_id) 
        
        return # IMPORTANT: Exit this on_message handler after processing the '!start' command.

    # --- Step 2: Handle messages from users currently awaiting a course ID ---
    # This block prevents the course ID itself from being processed as a chat message.
    if user_id in awaiting_course_id_users:
        # This message is the course ID response to a previous '!start' command.
        # It has already been (or will be) handled by the `client.wait_for` in the
        # other concurrent `on_message` invocation (the one that handled `!start`).
        # Therefore, this current `on_message` invocation (triggered by the course ID message itself)
        # should simply be ignored to prevent duplicate processing or misinterpretation.
        return # Ignore this message, it's part of the setup flow.

    # --- Step 3: Handle normal conversational messages ---
    # This block is only reached if the message was NOT '!start'
    # and the user is NOT currently awaiting a course ID.
    if user_id in discord_user_course_ids:
        course_id = discord_user_course_ids[user_id]
        try:
            reply = handle_message(user_id, course_id, msg_text) # Call the unified handle_message
            await message.channel.send(f"🤖 {reply}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
    else:
        # If the user has no stored course ID and didn't use '!start' or isn't awaiting, prompt them.
        await message.channel.send("❗ Please start a session first using `!start`.")

# This line starts the Discord bot and keeps it running.
client.run(DISCORD_BOT_TOKEN)