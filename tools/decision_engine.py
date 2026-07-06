"""
Decision Engine Module.

Uses the Universal Provider to evaluate a task against available skills
and decide the best course of action using Native Function Calling.
"""

import json
from typing import Optional, Dict, Any
from .skill_registry import SkillRegistry
from providers import UniversalProvider

class DecisionEngine:
    """
    Evaluates tasks and selects appropriate skills using an LLM.
    """
    
    def __init__(self, registry: SkillRegistry, llm_provider: Optional[UniversalProvider] = None) -> None:
        """
        Initialize the Decision Engine.

        Args:
            registry (SkillRegistry): The registry containing available skills.
            llm_provider (Optional[UniversalProvider]): The LLM provider to use for decision making.
        """
        self.registry = registry
        if llm_provider:
            self.llm = llm_provider
        else:
            from cli.chat import CURRENT_PROVIDER, CURRENT_MODEL
            provider = CURRENT_PROVIDER or "gemini"
            model = CURRENT_MODEL or "gemini-2.5-flash"
            self.llm = UniversalProvider(provider_name=provider, model_name=model)
        
    def decide_skill(self, user_prompt: str) -> Dict[str, Any]:
        """
        Decide which skill to use based on the user's prompt using Function Calling.

        Args:
            user_prompt (str): The user's task or query.

        Returns:
            Dict[str, Any]: A dictionary containing 'skill', 'arguments', and 'analysis'.
        """
        tools = self.registry.get_all_tool_schemas()
        
        # System instructions with heuristics
        system_msg = (
            "You are an intelligent orchestrator agent. "
            "Analyze the user's prompt and decide if you need to use any available tools.\n"
            "HEURISTICS:\n"
            "- If the task involves searching the web, navigating websites, or interacting with web content, ALWAYS prioritize 'browser_automation'.\n"
            "- Only use 'computer_use' for purely local OS-level tasks.\n"
        )
        
        try:
            kwargs = {
                "model": self.llm.model_name,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_prompt}
                ]
            }
            if tools:
                kwargs["tools"] = tools
                
            api_response = self.llm.client.chat.completions.create(**kwargs)
            message = api_response.choices[0].message
            
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_call = message.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                return {
                    "skill": tool_name,
                    "arguments": tool_args,
                    "analysis": f"LLM decided to call {tool_name}"
                }
            else:
                return {
                    "skill": "UNKNOWN",
                    "arguments": {},
                    "analysis": "No tool call was made.",
                    "response": message.content
                }
        except Exception as e:
            return {
                "skill": "UNKNOWN",
                "arguments": {},
                "analysis": f"API error during decision making: {e}"
            }
