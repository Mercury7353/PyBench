import traceback
from typing import Any, Dict, List, Optional, Tuple, Union

import openai
from loguru import logger
from openai.types.chat.chat_completion import (
    ChatCompletionMessage as OpenAIMessage,
)
from tenacity import retry, stop_after_attempt, wait_random

from llms.api_key_pool import SpinPool
from llms.base_llm import BaseLLM, LLMConfig
from llms.schema import DebugInfo, Message, Tool
from llms.utils import message2dict, tool2dict


class OpenAIAPI(BaseLLM):
    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self.pool = SpinPool(config["client_args"])

    def get_client_args(self):
        return self.pool

    def generate(
        self,
        messages: List[Union[Message, Dict]],
        tools: Optional[List[Union[Tool, Dict]]] = None,
    ) -> Tuple[Message, DebugInfo]:
        if len(messages) > 0 and isinstance(messages[0], Message):
            kwargs = dict(
                messages=[message2dict(msg) for msg in messages],
            )
        elif isinstance(messages[0], dict):
            kwargs = dict(
                messages=messages,
            )
        kwargs.update(self.config["model_args"])
        if tools is not None:
            if len(tools) > 0 and isinstance(tools[0], Tool):
                kwargs["tools"] = [tool2dict(tool) for tool in tools]
                kwargs["tool_choice"] = "auto"
            else:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

        new_message, debug_info = self._post_request(kwargs)

        new_message = Message(**new_message.model_dump())
        return new_message, debug_info

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=0.5, max=1.5))
    def _post_request(self, kwargs: Dict[str, Any]) -> Tuple[OpenAIMessage, DebugInfo]:
        try:
            with self.get_client_args() as client_args:
                logger.debug(f"getting client args: {client_args}")
                client = openai.OpenAI(
                    api_key=client_args.get("api_key", None),
                    base_url=client_args.get("base_url", None),
                )
                completion = client.chat.completions.create(**kwargs)
                logger.debug(f"{completion}")
        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit error: {e}")
            raise e
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {e}, type{e}, args{e.args}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e

        new_message = completion.choices[0].message
        return new_message, DebugInfo(
            info={"OpenAICompletion": completion.model_dump()}
        )
