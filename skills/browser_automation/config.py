"""
Configuration module for Browser Automation.

Handles environment variables, paths, and general settings required for
the browser automation module.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Suppress logs from browser_use
logging.getLogger("browser_use").setLevel(logging.CRITICAL)

# Load .env from the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(override=True, dotenv_path=PROJECT_ROOT / ".env")

def get_current_llm_config() -> dict:
    """
    Retrieve the current provider and model configuration from the main chat loop.

    Returns:
        dict: A dictionary containing provider, model, api_key, and base_url.
    """
    try:
        from cli.chat import CURRENT_PROVIDER, CURRENT_MODEL
        from providers.config import SUPPORTED_PROVIDERS
        
        provider = CURRENT_PROVIDER or "gemini"
        model = CURRENT_MODEL or "gemini-2.5-flash"
        
        config = SUPPORTED_PROVIDERS.get(provider.lower(), {})
        api_key = config.get("api_key")
        base_url = config.get("base_url")
        
        # If it's gemini but no key, fallback to env GEMINI_API_KEY for backward compatibility
        if provider.lower() == "gemini" and not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            
        return {
            "provider": provider.lower(),
            "model": model,
            "api_key": api_key,
            "base_url": base_url
        }
    except Exception as e:
        # Fallback to defaults
        return {
            "provider": "gemini",
            "model": "gemini-3.1-flash-lite",
            "api_key": os.environ.get("GEMINI_API_KEY"),
            "base_url": None
        }

def get_user_data_dir() -> str:
    """
    Get the path to the custom Chrome user data directory.
    Creates the directory if it does not exist.

    Returns:
        str: Absolute path to the user data directory.
    """
    user_data_dir = PROJECT_ROOT / "browser_profile" / "chrome" / "browser-use-user-data-dir-custom"
    os.makedirs(user_data_dir, exist_ok=True)
    return str(user_data_dir)

def get_chrome_executable_path() -> str:
    """
    Get the path to the Chrome executable.

    Returns:
        str: Absolute path to chrome.exe.
    """
    # Can be overridden via env var in the future.
    return os.getenv("CHROME_EXECUTABLE_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
