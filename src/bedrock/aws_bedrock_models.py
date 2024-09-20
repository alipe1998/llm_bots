import sys
import boto3
import json
from pathlib import Path
import os
from typing import List, Dict, Optional

aws_access_key_id = os.getenv("BOT_AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("BOT_AWS_SECRET_ACCESS_KEY")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
print(f"ROOT_DIR: {ROOT_DIR}")
sys.path.append(str(ROOT_DIR))

GPT_STATE_DIR = ROOT_DIR / 'gpt_state'

class BedrockCompletions:
    def __init__(
        self, 
        system_prompt: str = "You are a helpful assistant.", 
        model: str = "meta.llama3-70b-instruct-v1:0", 
        state_file: str = "bedrock_completions_state.json"
    ) -> None:
        """
        Initializes the BedrockCompletions class with AWS client, system prompt, model, and state file.

        Args:
            system_prompt (str): The initial system prompt for the assistant.
            model (str): The model ID from AWS Bedrock's list of approved models.
            state_file (str): The filename to store the state of message history.
        """
        self.client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="us-east-1",
        )
        self.state_file: Path = GPT_STATE_DIR / state_file
        self.model: str = model
        self.system_prompt: List[Dict[str, str]] = [{"text": system_prompt}] if system_prompt else []
        self.message_history: List[Dict[str, List[Dict[str, str]]]] = []
        self.load_state()

    def save_state(self, max_messages: int = 20) -> None:
        """
        Saves the message history to a file, truncating if there are more than a specified number of user messages.

        Args:
            max_messages (int): The maximum number of user messages to retain in the message history.
        """
        user_messages = [msg for msg in self.message_history if msg["role"] == "user"]
        
        if len(user_messages) > max_messages:
            self.message_history = self.message_history[-5:]

        with open(self.state_file, 'w') as f:
            json.dump(self.message_history, f)

    def clear_context(self) -> None:
        """
        Clears the context by resetting the message history and saving an empty state.
        """
        self.message_history = []
        with open(self.state_file, 'w') as f:
            json.dump(self.message_history, f)

    def load_state(self) -> None:
        """
        Loads the message history from a file if it exists and is not empty.
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    file_content = f.read().strip()

                    if not file_content:
                        self.message_history = []
                    else:
                        self.message_history = json.loads(file_content)
            except json.JSONDecodeError:
                print(f"WARNING: '{self.state_file}' contains invalid JSON. Initializing with an empty history.")
                self.message_history = []

    def send_message(self, user_input: str) -> Optional[str]:
        """
        Sends a user input message to the model and retrieves the assistant's response.

        Args:
            user_input (str): The user's input message to send to the model.

        Returns:
            Optional[str]: The assistant's response text or None if an error occurs.
        """
        self.message_history.append({
            "role": "user", 
            "content": [{"text": user_input}]
        })

        try:
            response = self.client.converse(
                modelId=self.model,
                messages=self.message_history,
                system=self.system_prompt,
                inferenceConfig={"maxTokens": 1000, "temperature": 0.5, "topP": 0.9},
                additionalModelRequestFields={}
            )

            assistant_message = response["output"]["message"]
            self.message_history.append(assistant_message)
            self.save_state()

            return assistant_message['content'][0]['text']

        except Exception as e:
            print(f"ERROR: Can't invoke '{self.model}'. Reason: {e}")
            return None

    def get_message_history(self) -> List[Dict[str, List[Dict[str, str]]]]:
        """
        Returns the current message history.

        Returns:
            List[Dict[str, List[Dict[str, str]]]]: The list of messages in the conversation history.
        """
        return self.message_history
