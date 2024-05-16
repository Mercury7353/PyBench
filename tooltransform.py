#!/usr/bin/env python
# encoding: utf-8
"""
format input messages, global_arguments, tools, tool_choice to a input string
"""
import json
import random
import re
from typing import List, Dict, Optional, Union
from io import StringIO
import ast
import traceback
import logging

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

t2t = {"integer": "int", "string": "str", "number": "float", "boolean": "bool"}


def message_format(msg):
    """https://github.com/facebookresearch/llama/blob/main/llama/generation.py#L343"""
    if msg["role"] == "assistant":
        #msg["tool_call_string"] = ""
        content = msg.get("content", "")
        if content is None:
            content = ""
        if "tool_calls" in msg and len(msg["tool_calls"]) > 0:

            def add_quotes(variable):
                if isinstance(variable, str):
                    return repr(variable)
                else:
                    return str(variable)

            tool_calls = []
            for tool_call in msg["tool_calls"]:
                tool_name = tool_call["name"]
                if "arguments" not in tool_call or tool_call["arguments"] is None:
                    continue
                if isinstance(tool_call["arguments"], str):
                    try:
                        tool_call["arguments"] = json.loads(tool_call["arguments"])
                    except:
                        continue
                args = ",".join([k + "=" + add_quotes(v) for k, v in tool_call["arguments"].items()])
                tool_calls.append(f"{tool_name}({args})")

            content += "<|tool_call|>" + "\n".join(tool_calls).strip()
            msg["tool_call_string"] = "\n".join(tool_calls).strip()
            msg["content"] = content
            assmsg={"role":"assistant","content":content}
            msg=assmsg

    return msg


def merge_messages(messages):
    """convert system message to user message, merge continous user message into one user message"""
    new_messages = []
    pre_role = ""
    for msg in messages:
        # system message should be merged with user message
        # reference: https://github.com/facebookresearch/llama/blob/main/llama/generation.py#L324
        if msg["role"] == "system":
            role = "user"
            content = msg["content"]
        else:
            role = msg["role"]
            content = msg["content"]

        if role == pre_role:
            new_messages[-1]["content"] += "\n" + content
        else:
            new_messages.append({"role": role, "content": content})
        pre_role = role
    # logger.info(f"merge {len(messages)} {len(new_messages)} messages")
    return new_messages


def transform_function(function: dict):
    """turn json format of function into signature"""
    classes = []
    res = "def {f_name}({ps}):"
    p_msgs = []
    props = function["parameters"]["properties"]
    f_des = function.get("description", "")
    for prop in props.keys():
        p_name = prop
        p_des = props[prop].get("description", "")
        p_type = t2t.get(props[prop]["type"], props[prop]["type"])
        p_type = generate_class(p_name, props[prop], classes)
        # print(p_name, function['parameters'].get('required', []))
        if (
            "required" in function["parameters"]
            and function["parameters"]["required"] is not None
            and p_name not in function["parameters"].get("required", [])
        ):
            p_type = f"Optional[{p_type}]"
        p_msgs.append([p_name, p_type, p_des])
    ps = ", ".join([p[0] + ": " + p[1] for p in p_msgs])
    # print(p_msgs)
    args = "\n".join(["    " + p[0] + " (" + p[1] + "): " + p[2] for p in p_msgs])
    res = res.format(f_name=function["name"], ps=ps)
    res += "\n"
    lint_msg = f'    """\n    {f_des}\n    Args:\n{args}\n    """'
    res += lint_msg
    if len(classes) > 0:
        res = "\n\n".join(classes) + "\n\n" + res
    return res


def generate_class(class_name, class_json, generated_classes=[]):
    # print(f"generating {class_name}\n", class_json)
    class_type = t2t.get(class_json["type"], class_json["type"])
    if "enum" in class_json:
        class_name = generate_type_name(class_name)
        class_string = f"class {class_name}({class_type}, Enum):\n"
        for i, val in enumerate(class_json["enum"]):
            if class_type == "str":
                class_string += f"    val{i} = '{val}'\n"
            else:
                class_string += f"    val{i} = {val}\n"
        generated_classes.append(class_string)
    elif class_type == "array":
        if "items" in class_json:
            class_name = generate_class(class_name, class_json["items"], generated_classes)
            class_name = f"List[{class_name}]"
        else:
            class_name = f'List[{class_json["type"]}]'
    elif class_type == "object":
        class_name = generate_type_name(class_name)
        class_string = f"class {class_name}(BaseModel):\n"
        for key, value in class_json.get("properties", {}).items():
            attr_class_name = generate_class(key, value, generated_classes)
            if key not in class_json.get("required", []):
                attr_class_name = f"Optional[{attr_class_name}]"
            if "description" in value:
                class_string += f"    {key}: {attr_class_name} # {value['description']}\n"
            else:
                class_string += f"    {key}: {attr_class_name}\n"
        generated_classes.append(class_string)
    else:
        class_name = class_type
    return class_name


def generate_type_name(type_string):
    parts = type_string.split("_")
    parts = [part[0].upper() + part[1:] for part in parts]
    return "".join(parts)


def my_input_format(
    messages: List[Dict],
    tools: List[Dict],
    tool_choice: Optional[Dict],
    output: Optional[Dict],
):
    """
    Process the input messages, global_arguments, tools, tool_choice,
        and convert it into a input string.
    The global arguments and tools can not be both empty.
    parameters:
        messages: List[Dict]
            the input messages
            For example:
        tools: List[Dict]
            the tools list you can use
            For example:
        tool_choice: Optional[Dict]
            choose a specific tool to use
            For example:
    """
    if tools is not None and len(tools) > 0:
        header = "from enum import Enum\nfrom typing import List, Dict, Optional\nfrom pydantic import BaseModel\n\n"
        tools_string = header
        for tool in tools:
            try:
                tools_string += "\n\n" + transform_function(tool)
            except:
                pass
        tools_template = "根据需要使用以下工具，如果用户的问题可以通过调用以下函数解决，请将函数调用的代码拼在<|tool_call|>后面返回。\n```\n{tools}\n```"
        tools_string = tools_template.format(tools=tools_string).strip()
    else:
        tools_string = ""
    if tool_choice is not None and "name" in tool_choice:
        tool_choice_template = "你必须使用{tool_choice}工具。"
        tool_choice_string = tool_choice_template.format(tool_choice=tool_choice["name"]).strip()
    else:
        tool_choice_string = ""

    system_suffix = tools_string + "\n" + tool_choice_string

    dialog = messages
    if tools_string != "":
        dialog = add_system_suffix(dialog, system_suffix)
    if output is not None:
        output["role"] = "assistant"
        dialog.append(output)

    return [message_format(msg) for msg in dialog]


def add_system_suffix(messages, system_suffix):
    idx = -1
    for i, msg in enumerate(messages):
        if msg["role"] == "system":
            idx=i
            msg['content']+="\n"+system_suffix
            break
            first, second = system_suffix.split("<|tool_call|>", 1)
            msg["content"] += "\n" + first
            msg["tool_call_string"] = second
            idx = i
            break
    if idx == -1:
        first, second = system_suffix.split("<|tool_call|>", 1)
        messages.insert(0, {"role": "system", "content": first, "tool_call_string": second})
    return messages


def convert_function_call_to_json(string):
    # print('converting', string)
    try:
        tool_calls = []
        x = ast.parse(string)
        for tool in x.body:
            function_name = tool.value.func.id
            function_args = {}
            for keyword in tool.value.keywords:
                function_args[keyword.arg] = ast.literal_eval(keyword.value)
            this_one = {"name": function_name, "arguments": function_args}
            # print('converted to', this_one)
            tool_calls.append(this_one)
        return tool_calls
    except Exception as e:
        return []


def fc2dict(sequence: str, spliter="<|tool_call|>"):
    if spliter in sequence:
        content, tool_call_string = sequence.split(spliter, 1)
        try:
            tool_call_pattern = r"\w+\([.\s\S]*\)"
            tool_calls = []
            for match in re.finditer(tool_call_pattern, tool_call_string):
                tool_call = match.group()
                tool_call_dicts = convert_function_call_to_json(tool_call)
                tool_calls.extend(tool_call_dicts)
            return {
                "content": content.strip(),
                "tool_calls": tool_calls,
                "role": "assistant",
            }
        except:
            return {"content": content.strip(), "role": "assistant"}
    else:
        return {"content": sequence.strip(), "role": "assistant"}


def main():
    function = {
        "name": "test",
        "description": "This is a test function",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "object",
                    "description": "a parameter description",
                    "properties": {
                        "a1": {"type": "number", "description": "a1 parameter description"},
                        "a2": {"type": "boolean", "description": "a2 parameter description"},
                    },
                },
                "b": {
                    "type": "array",
                    "description": "b parameter description",
                    "items": {
                        "type": "object",
                        "properties": {
                            "c": {"type": "integer", "description": "c parameter description"},
                            "d": {"type": "number", "description": "d parameter description"},
                        },
                    },
                },
                "c": {"type": "string", "description": "c parameter description"},
            },
            "required": ["a"],
        },
    }
    function_string = transform_function(function)
    print(function_string)


def transform(data, num_sample: int, r: random.Random):
    # messages = data.pop('message')
    # data['messages'] = messages
    drop_system_prob = 0.1
    use_tool_choice_prob = 0.05
    try:
        # step 1: drop system prompt with probability 0.1
        if len(data["messages"]) > 0 and data["messages"][0]["role"] == "system":
            if r.random() < drop_system_prob:
                data["messages"] = data["messages"][1:]
        # step 2: use tool_choice with probability 0.05
        # 20240311: not using this anymore
        # tool choice will be implemented in the model service
        # for i, msg in enumerate(data["messages"]):
        #     if msg["role"] == "user" and i < len(data["messages"]) - 1:
        #         next_msg = data["messages"][i + 1]
        #         if next_msg["role"] == "assistant" and "tool_calls" in next_msg and len(next_msg["tool_calls"]) > 0:
        #             tool_name = next_msg["tool_calls"][0]["name"]
        #             if r.random() < use_tool_choice_prob:
        #                 msg["content"] += f"你必须使用{tool_name}工具。"
        # step 3: transform messages, convert tools and tool_calls to string
        messages = my_input_format(data["messages"], tools=data.get("tools", None), tool_choice=None, output=None)
        # step 4: return
        return {"messages": messages}
    except:
        logger.error(traceback.format_exc())
        logger.info("error in functioncall transform")
        return {"messages": None}


if __name__ == "__main__":
    main()
