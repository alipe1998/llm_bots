from pathlib import Path
import sys
from openai import OpenAI
import json
from typing import List, Dict, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

GPT_STATE_DIR = ROOT_DIR / 'gpt_state'
GPT_STATE_DIR.mkdir(exist_ok=True)  # Ensure the directory exists

class GPTAssistant:
    def __init__(
        self, 
        assistant_name: str, 
        instructions: str, 
        model: str = "gpt-4o-mini", 
        state_file: str = "assistant_state.json"
    ) -> None:
        """
        Initializes the GPTAssistant with an assistant name, instructions, model, and state file.

        Args:
            assistant_name (str): The name of the assistant.
            instructions (str): Instructions for the assistant.
            model (str): The model ID for the assistant. Default is "gpt-4o-mini".
            state_file (str): The filename to store the assistant's state. Default is "assistant_state.json".
        """
        self.client = OpenAI()
        self.state_file: Path = GPT_STATE_DIR / state_file
        self.assistant = None
        self.thread = None
        self.load_state()

        if not self.assistant or not self.thread:
            self.assistant = self.client.beta.assistants.create(
                name=assistant_name,
                instructions=instructions,
                tools=[{"type": "code_interpreter"}],
                model=model,
            )
            self.thread = self.client.beta.threads.create()

    def save_state(self) -> None:
        """
        Save the assistant and thread state to a file.
        """
        state = {
            "assistant_id": self.assistant.id,
            "thread_id": self.thread.id
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def load_state(self) -> None:
        """
        Load the assistant and thread state from a file if it exists.
        """
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.assistant = self.client.beta.assistants.retrieve(assistant_id=state["assistant_id"])
                self.thread = self.client.beta.threads.retrieve(thread_id=state["thread_id"])

    def send_message(self, user_input: str) -> str:
        """
        Sends a user input message to the assistant and retrieves the assistant's response.

        Args:
            user_input (str): The user's input message to send to the assistant.

        Returns:
            str: The assistant's response or a message indicating the assistant is still processing.
        """
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_input
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions="Help the user with general questions"
        )

        self.save_state()

        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            return messages.data[0].content[0].text.value
        else:
            return "Assistant is still processing..."

    def get_message_history(self) -> List[Dict[str, Optional[str]]]:
        """
        Get the message history of the assistant's current thread.

        Returns:
            List[Dict[str, Optional[str]]]: A list of message dictionaries containing role, content, and timestamp.
        """
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            return [
                {
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.created_at
                }
                for message in messages
            ]
        else:
            return "No thread available to retrieve message history."

class GPTCompletions:
    def __init__(
        self, 
        instructions: str, 
        model: str = "gpt-4o-mini", 
        state_file: str = "gpt_completions_state.json",
        temperature: float = 2
    ) -> None:
        """
        Initializes the GPTCompletions with instructions, model, and state file.

        Args:
            instructions (str): Instructions for the assistant.
            model (str): The model ID for the assistant. Default is "gpt-4o-mini".
            state_file (str): The filename to store the message history. Default is "gpt_completions_state.json".
        """
        self.client = OpenAI()
        self.state_file: Path = GPT_STATE_DIR / state_file
        self.message_history: List[Dict[str, str]] = []
        self.load_state()
        self.model = model
        self.temperature = temperature

        if not self.message_history:
            system_message = {"role": "system", "content": instructions}
            self.message_history.append(system_message)

    def save_state(self) -> None:
        """
        Save the message history to a file.
        """
        with open(self.state_file, 'w') as f:
            json.dump(self.message_history, f)

    def load_state(self) -> None:
        """
        Load the message history from a file if it exists.
        """
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.message_history = json.load(f)

    def send_message(self, user_input: str) -> str:
        """
        Sends a user input message to the assistant and retrieves the assistant's response.

        Args:
            user_input (str): The user's input message to send to the assistant.

        Returns:
            str: The assistant's latest response.
        """
        self.message_history.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.message_history,
            temperature=self.temperature
        )

        assistant_message = response.choices[0].message.content
        self.message_history.append({"role": "system", "content": assistant_message})

        self.save_state()

        return assistant_message

    def get_message_history(self) -> List[Dict[str, str]]:
        """
        Returns the message history.

        Returns:
            List[Dict[str, str]]: The list of messages in the conversation history.
        """
        return self.message_history
