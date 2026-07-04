"""
Unified LLM Provider module.

This module provides a UniversalProvider class that uses the OpenAI-compatible API
to interact with various LLM providers (Gemini, OpenAI, Groq, Custom, etc.) 
through a single unified interface.
"""

import os
import json
from typing import List, Dict, Any, Generator
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv(override=True)

from .config import SUPPORTED_PROVIDERS

def get_available_models(provider_name: str) -> List[str]:
    """Fetch available models for a given provider dynamically."""
    if OpenAI is None:
        return []
        
    config = SUPPORTED_PROVIDERS.get(provider_name.lower())
    if not config:
        return []
        
    api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
    base_url = config.get("base_url")
    
    # If no API key is available, we might not be able to fetch models
    if not api_key and provider_name.lower() != "custom":
        # Let it try anyway, as some local providers (like Ollama) might not need an API key
        pass
        
    try:
        # Short timeout so the CLI doesn't hang forever
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=5.0)
        models = client.models.list()
        # Sort model IDs alphabetically
        return sorted([m.id for m in models.data])
    except Exception as e:
        return []


class UniversalProvider:
    """
    A unified provider class for interacting with any OpenAI-compatible API.
    """
    def __init__(self, provider_name: str, model_name: str, history_file: str = None) -> None:
        if OpenAI is None:
            raise ImportError("Please install openai package: pip install openai")
            
        self.provider_name = provider_name.lower()
        self.model_name = model_name
        
        # Use env var for history file if not explicitly provided
        if history_file is None:
            history_file = os.environ.get("PUMEN_HISTORY_FILE", "chat_history.json")
        self.history_file = history_file
        
        # Ensure the directory exists
        hist_dir = os.path.dirname(self.history_file)
        if hist_dir:
            os.makedirs(hist_dir, exist_ok=True)
        self.system_instruction = "Your name is Pumen, an exclusive smart AI assistant created by Pumen."
        
        provider_config = SUPPORTED_PROVIDERS.get(self.provider_name, SUPPORTED_PROVIDERS["openai"])
        
        # Use the pre-fetched values from the configuration
        api_key = provider_config.get("api_key") or os.environ.get("OPENAI_API_KEY")
        base_url = provider_config.get("base_url")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
        self.messages = self._load_history()
        if not self.messages:
            self.messages = [{"role": "system", "content": self.system_instruction}]

    def _load_history(self) -> List[Dict[str, str]]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                from rich.console import Console
                Console().print(f"\n[bold yellow]Old history corrupted ({e}). Resetting chat session![/]")
                try:
                    os.remove(self.history_file)
                except:
                    pass
        return []

    def _save_history(self) -> None:
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def send_message(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages
            )
            reply = response.choices[0].message.content or ""
            self.messages.append({"role": "assistant", "content": reply})
            self._save_history()
            return reply
        except Exception as e:
            self.messages.pop() # revert user message
            return f"Error from Provider {self.provider_name}: {str(e)}"

    def send_message_stream(self, message: str) -> Generator[str, None, None]:
        self.messages.append({"role": "user", "content": message})
        try:
            response_stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                stream=True
            )
            reply = ""
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        reply += content
                        yield content
            self.messages.append({"role": "assistant", "content": reply})
            self._save_history()
        except Exception as e:
            self.messages.pop() # revert user message
            yield f"\nError from Provider {self.provider_name}: {str(e)}"

    def reset_chat(self) -> None:
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        self.messages = [{"role": "system", "content": self.system_instruction}]
