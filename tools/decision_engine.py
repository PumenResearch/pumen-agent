"""
Decision Engine Module.

Uses the Gemini provider to evaluate a task against available skills
and decide the best course of action.
"""

import json
from typing import Optional, Dict
from .prompt_builder import PromptBuilder
from .skill_registry import SkillRegistry
from providers.gemini.client import GeminiProvider

class DecisionEngine:
    """
    Evaluates tasks and selects appropriate skills using an LLM.
    """
    
    def __init__(self, registry: SkillRegistry, llm_provider: Optional[GeminiProvider] = None) -> None:
        """
        Initialize the Decision Engine.

        Args:
            registry (SkillRegistry): The registry containing available skills.
            llm_provider (Optional[GeminiProvider]): The LLM provider to use for decision making.
        """
        self.prompt_builder = PromptBuilder(registry)
        # Initialize a dedicated LLM instance for decision making
        self.llm = llm_provider or GeminiProvider(model_name="gemini-2.5-flash")
        
    def decide_skill(self, user_prompt: str) -> Dict[str, str]:
        """
        Decide which skill to use based on the user's prompt.

        Args:
            user_prompt (str): The user's task or query.

        Returns:
            Dict[str, str]: A dictionary containing 'analysis' and 'skill'.
        """
        prompt = self.prompt_builder.build_decision_prompt(user_prompt)
        
        # Send the prompt to the LLM to get the decision
        response = self.llm.send_message(prompt)
        
        # Clean the response to parse JSON safely
        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            elif clean_response.startswith("```"):
                clean_response = clean_response[3:]
                
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
                
            decision = json.loads(clean_response.strip())
            return {
                "analysis": decision.get("analysis", "No analysis provided."),
                "skill": decision.get("skill", "UNKNOWN")
            }
        except Exception as e:
            return {
                "analysis": f"Failed to parse LLM response: {e}. Raw response: {response}",
                "skill": "UNKNOWN"
            }
