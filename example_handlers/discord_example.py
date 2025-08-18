# Import the run_discord_handler function
from maeser.discord import run_discord_handler

# Run the handler.
# Optional course_id and bot_token parameters can be provided, but these
# fields will be pulled from config.yaml by default.
# NOTE: Be sure to run this python script from the same directory where
# config.yaml is located.
run_discord_handler()
