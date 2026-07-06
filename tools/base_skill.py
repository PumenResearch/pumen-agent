from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseSkill(ABC):
    @classmethod
    @abstractmethod
    def get_tool_schema(cls) -> Dict[str, Any]:
        """Trả về schema chuẩn OpenAPI/JSON Schema cho Function Calling/MCP."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Thực thi logic của skill và trả về kết quả."""
        pass
