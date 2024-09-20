from pathlib import Path
import sys
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from flask import Flask, request, Response
import json

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from src.chatgpt import GPTAssistant, GPTCompletions  # Import the GPTAssistant class

# Initialize Slack Bolt App with your bot token and signing secret
app = App(token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))

# Initialize the Flask app for handling the challenge verification
flask_app = Flask(__name__)

# Initialize the GPTAssistant
assistant_name = "Obi"
instructions = "Help the user with general questions"
gpt_completions = GPTCompletions(instructions)

# Event listener for messages
@app.message("")
def handle_message(event, say):
    user_input = event.get('text', '')
    channel_id = event.get('channel')

    try:
        # Send the user message to GPTAssistant and get the response
        assistant_reply = gpt_completions.send_message(user_input)

        # Split and send the response in chunks if necessary
        for i in range(0, len(assistant_reply), 4000):  # Slack limit is 4000 characters
            chunk = assistant_reply[i:i + 4000]
            say(text=chunk, channel=channel_id)

    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
    except Exception as e:
        print(f"There was a problem calling the OpenAI API: {e}")

# Route to handle Slack events and challenge verification
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # Parse the request payload
    event_data = request.get_json()

    # Handle Slack challenge verification
    if "challenge" in event_data:
        return Response(event_data["challenge"], status=200, mimetype="text/plain")

    # Let Bolt handle the other events (if it's not a challenge request)
    return app.server.dispatch(request)

# Run the Flask app to listen for Slack events
if __name__ == "__main__":
    flask_app.run(port=3000)