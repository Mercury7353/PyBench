from llms.base_llm import BaseLLM
from llms.llmcenter import LLMCenter
from llms.openai_api import OpenAIAPI
from typing import Dict, Any

__all__ = ["BaseLLM", "LLMCenter", "OpenAIAPI"]


def build_llm(llm_type: str, config: Dict[str, Any]) -> BaseLLM:
    """build llm from config

    Args:
        llm_type (str): llm type, only support llmcenter and openai
        config (Dict[str, Any]): the dict of llm config

    Raises:
        ValueError: llm_type should be llmcenter or openai

    Returns:
        BaseLLM: LLMCenter or OpenAIAPI
    """
    if llm_type == "llmcenter":
        llm = LLMCenter(config)
    elif llm_type == "openai":
        llm = OpenAIAPI(config)
    else:
        raise ValueError("llm_type should be llmcenter or openai")
    return llm
