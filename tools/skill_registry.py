"""
Skill Registry Module.

Maintains a registry of available skills and their metadata. This registry
is used to inform the agent of what actions it can take.
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
    from the 'skills' directory.
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
        Scan the skills package and load any module that defines SKILL_METADATA.
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
                    # Check if the module exposes SKILL_METADATA
                    if hasattr(module, 'SKILL_METADATA'):
                        metadata = getattr(module, 'SKILL_METADATA')
                        name = metadata.get("name", module_name)
                        self._skills[name] = {
                            "name": name,
                            "description": metadata.get("description", "No description provided."),
                            "usage": metadata.get("usage", "No usage provided.")
                        }
                except Exception as e:
                    print(f"Failed to load skill module '{full_module_name}': {e}")
        
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """
        Retrieve all registered skills.

        Returns:
            List[Dict[str, Any]]: A list of skill metadata dictionaries.
        """
        return list(self._skills.values())
    
    def get_skill_descriptions(self) -> str:
        """
        Format all skills into a readable string for prompts.

        Returns:
            str: Formatted skill descriptions.
        """
        if not self._skills:
            return "No skills currently available."
            
        descriptions = []
        for name, info in self._skills.items():
            desc = f"- **{name}**: {info['description']}\n  *Usage*: {info['usage']}"
            descriptions.append(desc)
            
        return "\n".join(descriptions)
