from pathlib import Path
import sys
from typing import Optional, List, Dict

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from model_config import MODEL_CONFIG, CHANNEL_CONFIG
from src.chatgpt.chatgpt import GPTCompletions
from src.bedrock.aws_bedrock_models import BedrockCompletions

def chunk_message(message: str, chunk_size: int = 1990) -> List[str]:
    """
    Splits a message into chunks of a specified size and handles code blocks spanning across chunks.

    Args:
        message (str): The message to be split into chunks.
        chunk_size (int): The maximum size of each chunk. Defaults to 1990.

    Returns:
        List[str]: A list of message chunks.
    """
    chunks: List[str] = []
    open_code_block: bool = False  # Tracks if a code block is open
    
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i + chunk_size]
        if open_code_block:
            chunk = "\n```python\n" + chunk
        backtick_count = chunk.count("```")
        if backtick_count % 2 != 0:
            chunk += "\n```"
            open_code_block = True
        else:
            open_code_block = False
        chunks.append(chunk)
        
    return chunks

def handle_chunked_message(user_id: str, content: str, user_chunks: dict = None) -> Optional[str]:
    """
    Handle messages split into chunks.

    Args:
        user_id (str): The ID of the user sending the message.
        content (str): The content of the message, potentially split into chunks.
        user_chunks (dict, optional): A dictionary to store chunks for each user. Defaults to an empty dictionary.

    Returns:
        Optional[str]: The complete message when chunks are combined, or None if not yet complete.
    """
    if user_chunks is None:
        user_chunks = {}  # Initialize user_chunks if not provided

    if content.startswith("$$START$$"):
        user_chunks[user_id] = [content.replace("$$START$$", "").strip()]
    elif content.startswith("$$CONTINUE$$"):
        if user_id in user_chunks:
            user_chunks[user_id].append(content.replace("$$CONTINUE$$", "").strip())
    elif content.startswith("$$END$$"):
        if user_id in user_chunks:
            user_chunks[user_id].append(content.replace("$$END$$", "").strip())
            full_message = " ".join(user_chunks[user_id])
            del user_chunks[user_id]  # Clear the user's chunk storage
            return full_message

    return None

def initialize_models() -> Dict[str, object]:
    """Initialize models based on the provided configuration."""
    models: Dict[str, object] = {}  # Initialize the models dictionary here
    for model_name, config in MODEL_CONFIG.items():
        if config["class"] == "GPTCompletions":
            models[model_name] = GPTCompletions(config["system_prompt"])
        elif config["class"] == "BedrockCompletions":
            models[model_name] = BedrockCompletions(
                model=config["model"],
                system_prompt=config["system_prompt"],
                state_file=config["state_file"]
            )
    return models  # Return the initialized models