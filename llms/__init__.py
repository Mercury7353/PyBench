from llms.base_llm import BaseLLM

from llms.openai_api import OpenAIAPI
from typing import Dict, Any

__all__ = ["BaseLLM", "OpenAIAPI"]


def build_llm(llm_type: str, config: Dict[str, Any]) -> BaseLLM:
    """build llm from config

    Args:
        llm_type (str): llm type, only support  openai
        config (Dict[str, Any]): the dict of llm config

    Raises:
        ValueError: llm_type should be  openai

    Returns:
        BaseLLM:  OpenAIAPI
    """
    
    if llm_type == "openai":
        llm = OpenAIAPI(config)
    else:
        raise ValueError("llm_type should be llmcenter or openai")
    return llm
