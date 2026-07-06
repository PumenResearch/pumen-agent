"""
Computer Use Package.

Placeholder module for computer control tasks.
"""

from .skill import ComputerUseSkill

SKILL_METADATA = ComputerUseSkill.get_tool_schema()
SKILL_CLASS = ComputerUseSkill

__all__ = ["SKILL_METADATA", "SKILL_CLASS"]
