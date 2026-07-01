import json
from .skill_registry import SkillRegistry

class PromptBuilder:
    """
    Builder for generating decision-making prompts.
    """
    
    def __init__(self, registry: SkillRegistry) -> None:
        self.registry = registry
        self.base_instruction = (
            "You are an intelligent orchestrator agent. Your primary role is to "
            "analyze the user's prompt and decide which available skill is best suited "
            "to execute it.\n\n"
        )
        
    def build_decision_prompt(self, user_prompt: str) -> str:
        """
        Build the prompt instructing the LLM to analyze the request and choose a skill.

        Args:
            user_prompt (str): The raw prompt or query from the user.

        Returns:
            str: The fully constructed system prompt.
        """
        # Format the available skills as a JSON array for maximum clarity
        all_skills = self.registry.get_all_skills()
        skills_json_str = json.dumps(all_skills, ensure_ascii=False, indent=2)
        
        prompt = (
            f"{self.base_instruction}"
            "AVAILABLE SKILLS (JSON Format):\n"
            "Review the name, description, and usage requirements of each skill carefully:\n"
            f"{skills_json_str}\n\n"
            "INSTRUCTIONS:\n"
            "1. Analyze the user's prompt step-by-step.\n"
            "2. Compare the user's intent with the 'description' of the AVAILABLE SKILLS.\n"
            "3. Determine which skill matches best. If no skill fits perfectly, return 'UNKNOWN'.\n"
            "4. Return a JSON object with two keys: 'analysis' and 'skill'.\n"
            "   - 'analysis': Your reasoning for selecting or rejecting skills.\n"
            "   - 'skill': The exact 'name' of the chosen skill (or 'UNKNOWN').\n\n"
            f"USER PROMPT: {user_prompt}\n\n"
            "JSON RESPONSE:"
        )
        return prompt
