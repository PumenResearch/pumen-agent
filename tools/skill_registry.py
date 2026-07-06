"""
Skill Registry Module.

Maintains a registry of available skills and their metadata. This registry
is used to inform the agent of what actions it can take via Function Calling.
It automatically discovers skills from the 'skills' package.
"""

import os
import importlib
import pkgutil
from typing import List, Dict, Any
from pathlib import Path

class SkillRegistry:
    """
    Registry for managing available skills by auto-discovering them
    from the 'skills' directory and dispatching executions.
    """
    
    def __init__(self, skills_package: str = "skills") -> None:
        """
        Initialize the SkillRegistry and automatically load skills.
        
        Args:
            skills_package (str): The name of the Python package containing skills.
        """
        self._skills: Dict[str, Dict[str, Any]] = {}
        self.skills_package = skills_package
        self._discover_skills()
        
    def _discover_skills(self) -> None:
        """
        Scan the skills package and load any module that defines SKILL_METADATA and SKILL_CLASS.
        """
        try:
            # Import the root package for skills
            package = importlib.import_module(self.skills_package)
        except ImportError:
            # If the skills package doesn't exist, we just return empty
            return
            
        # Ensure the package has a __path__ attribute
        if not hasattr(package, '__path__'):
            return
            
        # Iterate through all submodules in the skills package
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if is_pkg:
                full_module_name = f"{self.skills_package}.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)
                    # Check if the module exposes SKILL_METADATA and SKILL_CLASS
                    if hasattr(module, 'SKILL_METADATA') and hasattr(module, 'SKILL_CLASS'):
                        schema = getattr(module, 'SKILL_METADATA')
                        skill_class = getattr(module, 'SKILL_CLASS')
                        
                        # In OpenAI schema, the name is in schema["function"]["name"]
                        if "function" in schema and "name" in schema["function"]:
                            name = schema["function"]["name"]
                        else:
                            name = schema.get("name", module_name)
                            
                        self._skills[name] = {
                            "name": name,
                            "schema": schema,
                            "class": skill_class
                        }
                except Exception as e:
                    print(f"Failed to load skill module '{full_module_name}': {e}")
        
    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Retrieve all registered skill schemas for Function Calling.

        Returns:
            List[Dict[str, Any]]: A list of skill schemas.
        """
        return [info["schema"] for info in self._skills.values()]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Dynamically execute a tool/skill by its name.
        
        Args:
            tool_name (str): The name of the skill to execute.
            **kwargs: Arguments to pass to the skill's execute method.
            
        Returns:
            Any: The result of the skill execution.
        """
        if tool_name not in self._skills:
            raise ValueError(f"Skill '{tool_name}' not found in registry.")
        
        skill_class = self._skills[tool_name]["class"]
        skill_instance = skill_class()
        return await skill_instance.execute(**kwargs)
