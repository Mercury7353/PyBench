from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from llms.schema import DebugInfo, Message, Tool

LLMConfig = Dict[str, Any]


class BaseLLM(ABC):
    def __init__(self, llm_config: LLMConfig):
        self.config = llm_config

    @abstractmethod
    def generate(
        self,
        messages: List[Union[Message, Dict]],
        tools: Optional[List[Union[Tool, Dict]]] = None,
    ) -> Tuple[Message, DebugInfo]:
        """接受用户传入的messages和tools[可选]，返回新的message和debug_info
        Args:
            messages: chatml messages
            tools = openai tools description
        Returns:
            new_message, debug_info
        """
        ...
