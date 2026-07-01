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

def get_gemini_api_key() -> str:
    """
    Retrieve and clean the Gemini API key from the environment.

    Returns:
        str: The cleaned Gemini API key.

    Raises:
        ValueError: If GEMINI_API_KEY is not found in the environment.
    """
    api_key_env = os.getenv("GEMINI_API_KEY")
    if not api_key_env:
        raise ValueError("GEMINI_API_KEY environment variable not found. Please add it to the .env file.")
    return api_key_env.strip(' "\'')

def get_user_data_dir() -> str:
    """
    Get the path to the custom Chrome user data directory.
    Creates the directory if it does not exist.

    Returns:
        str: Absolute path to the user data directory.
    """
    user_data_dir = PROJECT_ROOT / "browser-use-user-data-dir-custom"
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
