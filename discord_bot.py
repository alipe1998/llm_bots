import os
import discord
import src.utils.utils as utils
from model_config import CHANNEL_CONFIG
from typing import Optional

# Dictionary to store chunks per user
USER_CHUNKS: dict[int, list[str]] = {}

# Initialize models
MODELS = utils.initialize_models()

def create_discord_client() -> discord.Client:
    """
    Create and configure the Discord client.

    Returns:
        discord.Client: A configured instance of the Discord client.
    """
    intents = discord.Intents.default()
    intents.message_content = True
    return discord.Client(intents=intents)

# Initialize Discord client
client = create_discord_client()

async def send_reply(channel: discord.TextChannel, message: str) -> None:
    """
    Send the assistant's reply in chunks if necessary.

    Args:
        channel (discord.TextChannel): The channel to send the reply to.
        message (str): The message to be sent.
    """
    for chunk in utils.chunk_message(message):
        await channel.send(chunk)

@client.event
async def on_ready() -> None:
    """
    Event triggered when the bot is ready.
    """
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message: discord.Message) -> None:
    """
    Event triggered when a message is sent in a channel.

    Args:
        message (discord.Message): The message object that triggered the event.
    """
    if message.author == client.user:
        return

    user_id = message.author.id
    user_message = message.content
    channel_name = message.channel.name

    if channel_name not in CHANNEL_CONFIG:
        return  # Do nothing if the message is not in the specified channels

    model_key = CHANNEL_CONFIG[channel_name]
    model = MODELS[model_key]

    if user_message.startswith("$$START$$"):
        full_message = utils.handle_chunked_message(user_id, user_message, user_chunks=USER_CHUNKS)
        if full_message:
            try:
                assistant_reply = model.send_message(full_message)
                await send_reply(message.channel, assistant_reply)
            except Exception as e:
                await send_reply(message.channel, f"There was a problem calling the model: {e}")
    elif user_message.startswith("$$CLEAR CONTEXT$$"):
        model.clear_context()  # Clear context
        try:
            await send_reply(message.channel, 'Context Cleared.')
        except Exception as e:
            await send_reply(message.channel, f"There was a problem calling the model: {e}")
    else:
        try:
            assistant_reply = model.send_message(user_message)
            await send_reply(message.channel, assistant_reply)
        except Exception as e:
            await send_reply(message.channel, f"There was a problem calling the model: {e}")

def main() -> None:
    """
    Main function to run the bot.
    """
    token = os.getenv("DISCORD_BOT_TOKEN")
    try:
        client.run(token)
    except discord.errors.DiscordServerError as e:
        print(f"Discord server error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
