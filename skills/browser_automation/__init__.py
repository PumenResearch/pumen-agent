"""
Browser Automation Package.

This package provides modules for web browser automation tasks,
including configuration, browser setup, and agent execution.
"""

from .config import get_current_llm_config, get_user_data_dir, get_chrome_executable_path
from .browser_setup import kill_existing_chrome, create_browser_profile, initialize_browser
from .agent_runner import BrowserAgentRunner
from .skill import BrowserSkill

SKILL_METADATA = BrowserSkill.get_tool_schema()
SKILL_CLASS = BrowserSkill

__all__ = [
    "get_current_llm_config",
    "get_user_data_dir",
    "get_chrome_executable_path",
    "kill_existing_chrome",
    "create_browser_profile",
    "initialize_browser",
    "BrowserAgentRunner",
    "SKILL_METADATA",
    "SKILL_CLASS"
]
