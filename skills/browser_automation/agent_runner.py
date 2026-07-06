"""
Agent Runner Module.

Handles the creation and execution of the browser automation Agent
using the Gemini model.
"""

from typing import Any
from browser_use import Browser, Agent
from .config import get_current_llm_config

class BrowserAgentRunner:
    """
    A class to run browser automation tasks using the selected LLM.
    """

    def __init__(self, browser: Browser) -> None:
        """
        Initialize the BrowserAgentRunner.

        Args:
            browser (Browser): The Browser instance to use.
        """
        self.browser = browser
        config = get_current_llm_config()
        
        provider = config.get("provider", "openai")
        model = config["model"]
        api_key = config["api_key"]
        base_url = config.get("base_url")
        
        # All providers in Pumen Agent are standardized to use the OpenAI compatible API
        from browser_use import ChatOpenAI
        
        # Disable frequency_penalty as some OpenAI compatible endpoints (like Gemini) 
        # do not support it and will throw a 400 Bad Request error.
        kwargs = {
            "model": model, 
            "api_key": api_key,
            "frequency_penalty": None
        }
        if base_url:
            kwargs["base_url"] = base_url
            
        self.llm = ChatOpenAI(**kwargs)

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
