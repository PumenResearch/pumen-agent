"""
Gemini API client module.

This module provides the GeminiProvider class which wraps the google-genai library
to handle chat sessions, message sending, and chat history persistence.
"""

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
import threading
from typing import List, Dict, Any, Generator

AVAILABLE_MODELS: List[str] = ["Loading model list..."]

def _fetch_models() -> None:
    """Fetch the list of available Gemini models from the API."""
    global AVAILABLE_MODELS
    try:
        client = genai.Client()
        valid_models: List[str] = []
        for m in client.models.list():
            if not getattr(m, 'name', None):
                continue
            name = m.name.replace("models/", "")
            if 'gemini' in name and 'vision' not in name:
                valid_models.append(name)
        if valid_models:
            # Sort to keep the newer versions (2.5, 2.0) at the top
            AVAILABLE_MODELS = sorted(valid_models, reverse=True)
        else:
            AVAILABLE_MODELS = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    except Exception as e:
        from rich.console import Console
        Console().print(f"\n[bold red]⚠️ Error calling ModelService.ListModels: {e}[/]")
        Console().print("[italic gray]Your API key works for chat, but failed to fetch the model list. Using the default list instead.[/]")
        AVAILABLE_MODELS = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

def fetch_models_async() -> None:
    """Fetch the list of models asynchronously in the background to avoid blocking the UI."""
    threading.Thread(target=_fetch_models, daemon=True).start()

# Load environment variables from .env file
load_dotenv(override=True)

class GeminiProvider:
    """
    Provider class for interacting with the Gemini API using the google-genai library.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash", history_file: str = "chat_history.json") -> None:
        """
        Initialize the Gemini provider.

        Args:
            model_name (str): The name of the Gemini model to use.
            history_file (str): The file path where chat history is saved.
        """
        self.client = genai.Client()
        self.model_name = model_name
        self.history_file = history_file
        
        # Load chat history from file, if it exists
        history = self._load_history()
        
        # Initialize a new chat session with the loaded history
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            history=history,
            config={
                "system_instruction": "Your name is Pumen, an exclusive smart AI assistant created by Pumen. Absolutely never identify yourself as Gemini or a Google AI in any of your responses."
            }
        )

    def _load_history(self) -> List[Any]:
        """
        Load the chat history from the local JSON file.

        Returns:
            List[Any]: A list of chat history objects, or an empty list if loading fails.
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Clean the history data to prevent Pydantic validation errors on newer SDK versions
                    # We remove 'None' values and explicitly forbid known problematic keys
                    for msg in data:
                        if 'parts' in msg:
                            for part in msg['parts']:
                                keys_to_remove = [
                                    k for k, v in part.items() 
                                    if v is None or k in ['tool_call', 'tool_response', 'part_metadata', 'executable_code', 'code_execution_result']
                                ]
                                for k in keys_to_remove:
                                    part.pop(k, None)
                    return data
            except Exception as e:
                print(f"\n[bold yellow]Old history is corrupted or incompatible ({e}). Automatically resetting to a new chat session![/]")
                try:
                    os.remove(self.history_file)
                except:
                    pass
        return []

    def _save_history(self) -> None:
        """
        Save the current chat history to the local JSON file.
        """
        try:
            # Retrieve the history as a list of Content objects and dump to JSON
            contents = self.chat_session.get_history()
            
            # Use Pydantic's mode='json' to automatically convert complex data types (like bytes)
            # into JSON-serializable formats (usually strings)
            data: List[Dict[str, Any]] = []
            for c in contents:
                try:
                    data.append(c.model_dump(mode='json', exclude_none=True))
                except TypeError:
                    # Fallback if an older version of Pydantic does not support mode='json'
                    data.append(c.model_dump(exclude_none=True))
            
            # Create a Custom Encoder as a fallback in case bytes still remain
            class SafeEncoder(json.JSONEncoder):
                def default(self, obj: Any) -> Any:
                    if isinstance(obj, bytes):
                        return obj.decode('utf-8', errors='ignore')
                    return super().default(obj)
                    
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=SafeEncoder)
        except Exception as e:
            print(f"Error saving history: {e}")

    def send_message(self, message: str) -> str:
        """
        Send a synchronous message to the chat session.

        Args:
            message (str): The message to send.

        Returns:
            str: The text response from the model.
        """
        try:
            response = self.chat_session.send_message(message)
            self._save_history()
            return response.text
        except Exception as e:
            return f"Error from Gemini Provider: {str(e)}"

    def send_message_stream(self, message: str) -> Generator[str, None, None]:
        """
        Send a message and stream the response back.

        Args:
            message (str): The message to send.

        Yields:
            str: Chunks of the text response from the model.
        """
        try:
            response_stream = self.chat_session.send_message_stream(message)
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
            self._save_history()
        except Exception as e:
            yield f"\nError from Gemini Provider: {str(e)}"

    def reset_chat(self) -> None:
        """
        Clear the chat history and initialize a new chat session.
        """
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        self.chat_session = self.client.chats.create(model=self.model_name)
