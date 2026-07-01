"""
Agent Runner Module.

Handles the creation and execution of the browser automation Agent
using the Gemini model.
"""

from typing import Any
from browser_use import Browser, Agent, ChatGoogle
from .config import get_gemini_api_key

class BrowserAgentRunner:
    """
    A class to run browser automation tasks using the Gemini model.
    """

    def __init__(self, browser: Browser, model_name: str = "gemini-3.1-flash-lite") -> None:
        """
        Initialize the BrowserAgentRunner.

        Args:
            browser (Browser): The Browser instance to use.
            model_name (str): The name of the Gemini model to use.
        """
        self.browser = browser
        self.api_key = get_gemini_api_key()
        self.llm = ChatGoogle(model=model_name, api_key=self.api_key)

    async def run_task(self, task_description: str) -> Any:
        """
        Run a specific automation task.

        Args:
            task_description (str): Detailed instructions for the task.

        Returns:
            Any: The history or final result of the executed task.
        """
        agent = Agent(
            task=task_description,
            llm=self.llm,
            browser=self.browser
        )
        
        return await agent.run()
