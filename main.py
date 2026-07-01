"""
Main entry point for the Pumen Agent application.

This module is responsible for loading environment variables
and initializing the Command Line Interface (CLI) session.
"""

from dotenv import load_dotenv
import os
import logging
import warnings

# Suppress all noisy logs and warnings that might interfere with the CLI UI
os.environ["BROWSER_USE_LOGGING_LEVEL"] = "error"
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger().setLevel(logging.CRITICAL)

# Load environment variables from .env file, overriding system variables if they exist.
load_dotenv(override=True)

from cli.interface import display_welcome
from cli.chat import start_chat_session


def start_agent() -> None:
    """
    Initialize and start the Pumen Agent CLI application.

    This function displays the welcome interface and then starts
    the interactive chat session with the user.
    """
    display_welcome()
    start_chat_session()


if __name__ == "__main__":
    start_agent()