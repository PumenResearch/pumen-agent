"""
Configuration module for LLM Providers.

This module defines the supported providers and their default configurations.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Define supported providers and their default configurations
SUPPORTED_PROVIDERS = {
    "gemini": {
        "base_url": os.environ.get("GEMINI_BASE_URL"),
        "api_key": os.environ.get("GEMINI_API_KEY")
    },
    "openai": {
        "base_url": os.environ.get("OPENAI_BASE_URL"),
        "api_key": os.environ.get("OPENAI_API_KEY")
    },
    "groq": {
        "base_url": os.environ.get("GROQ_BASE_URL"),
        "api_key": os.environ.get("GROQ_API_KEY")
    },
    "custom": {
        "base_url": os.environ.get("CUSTOM_BASE_URL"),
        "api_key": os.environ.get("CUSTOM_API_KEY")
    }
}
