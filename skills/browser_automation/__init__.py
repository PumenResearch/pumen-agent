"""
Browser Automation Package.

This package provides modules for web browser automation tasks,
including configuration, browser setup, and agent execution.
"""

from .config import get_gemini_api_key, get_user_data_dir, get_chrome_executable_path
from .browser_setup import kill_existing_chrome, create_browser_profile, initialize_browser
from .agent_runner import BrowserAgentRunner

SKILL_METADATA = {
    "name": "browser_automation",
    "description": "Automate web browsing tasks like searching, clicking, and interacting with web pages.",
    "usage": "Provide a clear task description with steps and URLs to visit."
}

__all__ = [
    "get_gemini_api_key",
    "get_user_data_dir",
    "get_chrome_executable_path",
    "kill_existing_chrome",
    "create_browser_profile",
    "initialize_browser",
    "BrowserAgentRunner",
    "SKILL_METADATA"
]
