# teams_bot_runner.py
import asyncio
import os
from fastapi import FastAPI, Request, Response
import uvicorn
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes

# Import the core message handling logic and utilities from terminal_script
# This creates a dependency, ensuring terminal_script is loaded first.
from terminal_script import handle_message, get_valid_course_ids, global_maeser_sessions

# From config.py
from config import TEAMS_APP_ID, TEAMS_APP_PASSWORD

# FastAPI app instance
app = FastAPI()

# Bot Framework Adapter settings
# Ensure these match your Azure Bot Service App ID and Password
SETTINGS = BotFrameworkAdapterSettings(TEAMS_APP_ID, TEAMS_APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Teams-specific session tracking for user-selected course IDs
# {user_id: course_id}
teams_user_course_ids = {}

# Set to track users who are currently in the process of submitting a course ID
# This prevents their course ID input from being treated as a regular message.
awaiting_course_id_teams_users = set()

# Error handler for the Bot Framework Adapter
async def on_error(context: TurnContext, error: Exception):
    print(f"Unhandled Teams bot error: {error}")
    # Send a message to the user informing them of the error
    await context.send_activity("Oops! Something went wrong. Please try again.")

ADAPTER.on_turn_error = on_error

# The main endpoint for incoming messages from the Bot Framework Connector
@app.post("/api/messages")
async def messages(request: Request):
    # Parse the incoming request body
    if "application/json" in request.headers["Content-Type"]:
        body = await request.json()
    else:
        body = await request.body()
    
    activity = Activity().deserialize(body)
    auth_header = request.headers["Authorization"] if "Authorization" in request.headers else ""

    # Define the asynchronous turn handler logic
    async def turn_handler(turn_context: TurnContext):
        # Only process messages of type 'message'
        if turn_context.activity.type == ActivityTypes.message:
            user_id = turn_context.activity.from_property.id
            msg_text = turn_context.activity.text.strip()

            # --- Step 1: Handle '!start' command ---
            if msg_text.lower().startswith("!start"):
                if user_id in awaiting_course_id_teams_users:
                    await turn_context.send_activity("You are already in the process of starting a session. Please provide your course ID.")
                    return

                await turn_context.send_activity("🧑‍🏫 Please enter your course ID:")
                awaiting_course_id_teams_users.add(user_id) # Mark user as awaiting course ID
                return # Exit this turn_handler, as we are now awaiting a course ID

            # --- Step 2: Handle messages from users currently awaiting a course ID ---
            if user_id in awaiting_course_id_teams_users:
                # This message is expected to be the course ID
                course_id = msg_text.lower() # Normalize to lowercase for consistency

                valid_courses = get_valid_course_ids()
                if course_id not in valid_courses:
                    await turn_context.send_activity(f"❌ Invalid course ID. Available options: {', '.join(valid_courses)}")
                    # Keep user in awaiting state so they can try again
                    return

                teams_user_course_ids[user_id] = course_id # Store the chosen course_id
                await turn_context.send_activity(f"✅ Session started for course `{course_id}`! Send your question.")
                
                # IMPORTANT: Remove user from awaiting set after successfully getting course_id
                awaiting_course_id_teams_users.discard(user_id)
                return # Exit this turn_handler, as the course ID has been processed

            # --- Step 3: Handle normal conversational messages ---
            # This block is only reached if the message was NOT '!start'
            # and the user is NOT currently awaiting a course ID.
            if user_id in teams_user_course_ids:
                course_id = teams_user_course_ids[user_id]
                try:
                    reply = handle_message(user_id, course_id, msg_text) # Call the unified handle_message
                    await turn_context.send_activity(f"🤖 {reply}")
                except Exception as e:
                    await turn_context.send_activity(f"❌ Error: {e}")
            else:
                # If the user has no stored course ID and didn't use '!start' or isn't awaiting, prompt them.
                await turn_context.send_activity("❗ Please start a session first using `!start`.")
        
        # Handle other activity types (e.g., bot added to conversation)
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            if turn_context.activity.members_added:
                for member in turn_context.activity.members_added:
                    if member.id != turn_context.activity.recipient.id: # Check if the added member is not the bot itself
                        await turn_context.send_activity(f"Hello {member.name}! I am Maeser. Please type `!start` to begin a session and select a course.")
        # Add more activity types as needed (e.g., typing, end_of_conversation)
        elif turn_context.activity.type == ActivityTypes.typing:
            pass # Ignore typing activities
        elif turn_context.activity.type == ActivityTypes.end_of_conversation:
            pass # Ignore end of conversation activities
        # You can add other ActivityTypes handlers as necessary

    # Process the incoming activity with the Bot Framework Adapter
    response = await ADAPTER.process_activity(activity, auth_header, turn_handler)
    if response:
        return Response(content=response.body, status_code=response.status, headers={"Content-Type": response.headers["Content-Type"]})
    return Response(status_code=200)

# Function to run the FastAPI server for the Teams bot
# This function will be called by terminal_script.py in a separate thread.
def start_teams_bot_server(port: int = 3978):
    """Starts the FastAPI server for the Teams bot on the specified port."""
    print(f"Starting Teams bot FastAPI server on http://0.0.0.0:{port}")
    # The 'loop' argument is crucial when running uvicorn from within another asyncio loop or thread
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")