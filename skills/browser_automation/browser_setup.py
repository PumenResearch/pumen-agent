"""
Browser Setup Module.

Handles the initialization and configuration of the web browser, including
managing running instances and creating browser profiles.
"""

import os
import asyncio
from browser_use import Browser, BrowserProfile
from .config import get_user_data_dir, get_chrome_executable_path

async def kill_existing_chrome() -> None:
    """
    Forcefully close any existing Chrome instances to prevent file locks.
    """
    os.system("taskkill /F /IM chrome.exe /T > nul 2>&1")
    await asyncio.sleep(1)

def create_browser_profile(headless: bool = False) -> BrowserProfile:
    """
    Create and configure a BrowserProfile.

    Args:
        headless (bool): Whether to run the browser in headless mode.

    Returns:
        BrowserProfile: The configured browser profile.
    """
    return BrowserProfile(
        headless=headless,
        executable_path=get_chrome_executable_path(),
        user_data_dir=get_user_data_dir(),
        disable_security=True,
        keep_alive=True,
        extra_chromium_args=[
            "--enable-protected-audience-api",
            "--widevine-cdm-path"
        ]
    )

def initialize_browser(headless: bool = False) -> Browser:
    """
    Initialize the Browser instance with the configured profile.

    Args:
        headless (bool): Whether to run the browser in headless mode.

    Returns:
        Browser: The initialized Browser instance.
    """
    profile = create_browser_profile(headless=headless)
    return Browser(browser_profile=profile)
