"""llmcenter接口"""

import json
import logging
import traceback
from typing import Dict, List, Tuple, Union

import requests

"""
from adc.llms.base_llm import BaseLLM
from adc.register import register_llm

"""
from adc import (
    DebugInfo,
    Function,
    Message,
    RoleType,
    Tool,
    ToolCall,
    ToolProperty,
)

logger = logging.getLogger(__name__)


LLMCENTER_ROLE_MAP = {
    "user": "USER",
    "system": "SYSTEM",
    "assistant": "AI",
    "tool": "TOOL",
    "knowledge": "KNOWLEDGE",
}


# @register_llm("llmcenter")
class LLMCenter:
    def __init__(self, llm_config: Dict):
        """初始化

        Args:
            llm_config (Dict): 配置
        """
        # super().__init__(llm_config)
        self.app_code = llm_config.get("app_code")
        self.user_token = llm_config.get("user_token")
        self.token_url = llm_config.get("token_url")  # 获取app_token的url
        self.url = llm_config.get("url")  # 请求llm的url
        self.timeout = llm_config.get("timeout", 60)
        self.model = llm_config.get("model")
        self.modelId = self._get_model_id(self.model)
        self.app_token = self._update_app_token()
        self.frequency_penalty = llm_config.get("frequency_penalty", 1.0)
        self.max_tokens = llm_config.get("max_tokens", 1024)
        self.presence_penalty = llm_config.get("presence_penalty", 1.0)
        self.seed = llm_config.get("seed", None)
        self.temperature = llm_config.get("temperature", 0.9)
        self.top_p = llm_config.get("top_p", 0.9)

    def _get_model_id(self, model: str) -> int:
        """get model id

        Args:
            model (str): 模型名
                暂时支持gpt-4-32k/gpt-4/gpt-35-turbo-16k/gpt-35-turbo-0613

        Raises:
            ValueError: model不支持时抛出异常

        Returns:
            str: 返回模型id
        """
        if model == "gpt-4-32k":
            return 30
        elif model == "gpt-4":
            return 29
        elif model == "gpt-35-turbo-16k":
            return 31
        elif model == "gpt-35-turbo-0613":
            return 32
        else:
            raise ValueError(f"model {model} not supported")

    def _update_app_token(self) -> str:
        """获取app_token

        Args:
            app_code (str): app_code 需要时可以申请
            user_token (str): 用户token 在ModelBest运营平台可以查到

        Returns:
            str: 返回app_token 有效期为1小时
        """
        try:
            url = (
                f"{self.token_url}?appCode={self.app_code}"
                f"&userToken={self.user_token}&expTime=3600"
            )
            headers = {"User-Agent": "Apifox/1.0.0 (https://apifox.com)"}

            response = requests.request(
                "GET", url, headers=headers, data={}, timeout=self.timeout
            ).json()
            return response["data"]
        except requests.RequestException as e:
            print("error when getting app token", str(e))
            return "error"

    def _convert_messages(self, messages: List[Message]) -> List[Dict]:
        new_messages = []
        for msg in messages:
            new_msg = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.role.value == "assistant" and msg.tool_calls is not None:
                new_msg["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in msg.tool_calls
                ]
            if msg.role.value == "tool":
                new_msg["tool_call_id"] = msg.tool_call_id
            new_messages.append(new_msg)
        return new_messages

    def _convert_property(self, property: ToolProperty) -> Dict:
        new_property = {
            "type": property.type.value,
        }
        if property.description is not None:
            new_property["description"] = property.description
        if property.type.value == "object":
            new_property["properties"] = {
                key: self._convert_property(value)
                for key, value in property.properties.items()
            }
            if property.required is not None:
                new_property["required"] = property.required
        elif property.type.value == "array":
            new_property["items"] = self._convert_property(property.items)
        elif property.enum is not None:
            new_property["enum"] = property.enum
        return new_property

    def _convert_tools(self, tools: List[Tool]) -> List[Dict]:
        new_tools = []
        for tool in tools:
            new_tool = {
                "type": tool.type,
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description,
                    "parameters": self._convert_property(tool.function.parameters),
                },
            }
            new_tools.append(new_tool)
        return new_tools

    def _make_request(
        self,
        messages: List[Message],
        tools,
        tool_choice: Union[str, Dict] = None,
    ) -> Message:
        """发送请求

        Args:
            messages (List[Message]): 请求的消息
            tools (Optional[List[Tool]], optional): 请求需要的工具，可选项 Defaults to None.
            tool_choice (Union[str, Dict], optional): 是否指定工具，可以传str(auto或none)，也可以传dict。 Defaults to None.

        Returns:
            Message: 返回的消息
        """
        messages = self._convert_messages(messages)
        # tools = self._convert_tools(tools)
        _messages = []
        for msg in messages:
            if msg["role"] == "assistant" and "tool_calls" in msg:
                _messages.append(
                    {
                        "role": LLMCENTER_ROLE_MAP.get(msg["role"], msg["role"]),
                        "contents": [{"type": "TEXT", "pairs": msg["content"]}],
                        "toolCalls": [
                            {
                                "id": tool["id"],
                                "type": "FUNCTION",
                                "function": {
                                    "name": tool["function"]["name"],
                                    "arguments": tool["function"]["arguments"],
                                },
                            }
                            for tool in msg["tool_calls"]
                        ],
                    }
                )
            elif msg["role"] == "tool":
                _messages.append(
                    {
                        "role": LLMCENTER_ROLE_MAP.get(msg["role"], msg["role"]),
                        "toolCallId": msg["tool_call_id"],
                        "contents": [{"type": "TEXT", "pairs": msg["content"]}],
                    }
                )
            else:
                _messages.append(
                    {
                        "role": LLMCENTER_ROLE_MAP.get(msg["role"], msg["role"]),
                        "contents": [{"type": "TEXT", "pairs": msg["content"]}],
                    }
                )
        _tools = [
            {
                "type": "FUNCTION",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "OBJECT",
                        "properties": tool["parameters"]["properties"],
                        "required": tool["parameters"].get("required", []),
                    },
                },
            }
            for tool in tools
        ]
        if tool_choice == "none":
            _tool_choice = {"type": "NONE", "functionName": ""}
        elif tool_choice == "auto":
            _tool_choice = {"type": "AUTO"}
        elif isinstance(tool_choice, dict):
            _tool_choice = {"type": "AUTO", "functionName": tool_choice["name"]}
        else:
            _tool_choice = None

        payload = json.dumps(
            {
                "userSafe": 0,
                "aiSafe": 0,
                "modelId": self.modelId,
                "chatMessage": _messages,
                "tools": _tools,
                "toolChoice": _tool_choice,
                "modelParamConfig": {
                    "frequencyPenalty": self.frequency_penalty,
                    "maxTokens": self.max_tokens,
                    "presencePenalty": self.presence_penalty,
                    "seed": self.seed,
                    "temperature": self.temperature,
                    "topP": self.top_p,
                },
            }
        )
        headers = {
            "app-code": self.app_code,
            "app-token": self.app_token,
            "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
            "Content-Type": "application/json",
        }
        response = requests.request(
            "POST", self.url, headers=headers, data=payload
        ).json()
        # print("CheckPoint",response)
        msg = response["data"]["messages"][0]
        # print("Test",msg)
        if "toolCall" in msg and msg["toolCall"] is not None:
            msg = Message(
                role=RoleType.ASSISTANT,
                content=msg["content"] if msg["content"] is not None else "",
                tool_calls=[
                    ToolCall(
                        id=tool_call["id"],
                        type="function",
                        function=Function(
                            name=tool_call["function"]["name"],
                            arguments=json.dumps(
                                tool_call["function"]["arguments"], ensure_ascii=False
                            ),
                        ),
                    )
                    for tool_call in msg["toolCall"]
                ],
            )
            return msg
        else:
            return Message(role=RoleType.ASSISTANT, content=msg["content"])

    def chat(self, messages: List[Message], tools) -> Tuple[Message, DebugInfo]:
        """接受用户传入的messages和tools[可选]，返回新的message和debug_info
        tools:Optional[List[Tool]] = None,
        Args:
            messages: chatml messages
            tools = openai tools description
        Returns:
            new_message, debug_info
        """
        if tools is None:
            tools = []
        try:
            msg = self._make_request(messages, tools)
            return msg, DebugInfo(info={})
        except Exception as e:
            return Message(role="assistant", content=traceback.format_exc()), DebugInfo(
                info={
                    "LLMCenterError": str(e),
                    "LLMCenter_traceback": traceback.format_exc(),
                }
            )
