from typing import Any, Dict
from tools.base_skill import BaseSkill
from .browser_setup import initialize_browser
from .agent_runner import BrowserAgentRunner

class BrowserSkill(BaseSkill):
    @classmethod
    def get_tool_schema(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "browser_automation",
                "description": "Automate web browsing tasks like searching, clicking, and interacting with web pages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Detailed instructions for the web task, including URLs if applicable"
                        }
                    },
                    "required": ["task_description"]
                }
            }
        }

    async def execute(self, task_description: str, **kwargs) -> Any:
        browser = initialize_browser(headless=False)
        runner = BrowserAgentRunner(browser)
        history = await runner.run_task(task_description)
        return history.final_result()
