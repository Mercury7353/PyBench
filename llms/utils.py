from typing import Dict, Optional

from llms.schema import DataType, Message, Tool, ToolProperty


def property2dict(property_: ToolProperty) -> Dict:
    """把传入的ToolProperty转换为OpenAI接口需要的dict格式

    Args:
        property (ToolProperty): ToolProperty对话

    Returns:
        Dict: 参数的dict形式描述
    """
    new_property = {"type": property_.type.value}
    if property_.description is not None:
        new_property["description"] = property_.description
    if property_.type == DataType.OBJECT:
        new_property["properties"] = {
            key: property2dict(value) for key, value in property_.properties.items()
        }
        if property_.required is not None:
            new_property["required"] = property_.required
    elif property_.type == DataType.ARRAY:
        new_property["items"] = property2dict(property_.items)
    elif property_.enum is not None:
        new_property["enum"] = property_.enum
    return new_property


def tool2dict(tool: Tool) -> Dict[str, str]:
    parameters = property2dict(tool.function.parameters)
    parameters["type"] = DataType.OBJECT.name
    if "required" not in parameters:
        parameters["required"] = []
    new_tool = {
        "type": "function",
        "function": {
            "name": tool.function.name,
            "description": tool.function.description,
            "parameters": parameters,
        },
    }
    return new_tool


def message2dict(
    message: Message,
) -> Dict[str, Optional[str | list[Dict[str, str]]]]:
    ret = dict(
        role=message.role.value,
        content=message.content,
        tool_calls=[call.model_dump() for call in message.tool_calls]
        if message.tool_calls is not None
        else None,
        tool_call_id=message.tool_call_id,
    )
    ret = {k: v for k, v in ret.items() if v is not None}
    return ret
