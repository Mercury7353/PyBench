"""output parser for code interpreter"""

import ast
from typing import Tuple


def parse_code_action(
    output: str,
    mode: str = "prompt",
    code_start_token: str = "```\npython\n",
    code_end_token: str = "```",
    tool_call_token: str = "<|tool_call|>",
) -> Tuple[str, str]:
    """parse output from code interpreter

    Args:
        output (str): the output from code interpreter
        mode: the mode of the output, could be prompt, functioncall, assistant
        code_start_token: the token code script starts with, only used in prompt mode
        code_end_token: the token code script ends with, only used in prompt mode
        tool_call_token: the token for tool call, only used in prompt mode

    Returns:
        Tuple[str, str]: reasoning and code action
    """
    if mode == "prompt":
        return extract_code(output, code_start_token, code_end_token)
    elif mode == "functioncall":
        rsp = fc2dict(output, tool_call_token)
        if "tool_calls" in rsp and len(rsp["tool_calls"]) > 0:
            return rsp["content"], rsp["tool_calls"][0]["arguments"]["code"]
        else:
            return rsp["content"], ""
    elif mode == "assistant":
        raise NotImplementedError("assistant mode is not implemented yet")
    else:
        raise ValueError(f"mode {mode} is not supported")


def extract_code(
    rsp: str, code_start_token: str = "```\npython\n", code_end_token: str = "```"
) -> Tuple[str, str]:
    """extract code from assistant content

    Args:
        rsp (str): the response content from assistant
        code_start_token (str, optional): the token code script starts with. Defaults to "```\npython".
        code_end_token (str, optional): the token code script ends with. Defaults to "```".

    Returns:
        Tuple[str, str]: reasoning and code action
    """
    # TODO: implement the code extraction logic using different code_start_token and code_end_token
    rsp = str(rsp)

    start_index = rsp.find(code_start_token)
    if start_index == -1:
        return rsp, ""

    start_index += len(code_start_token)
    end_index = rsp.find(code_end_token, start_index)
    if end_index == -1:
        return rsp, ""

    return rsp[:start_index].replace(code_start_token, "").strip(), rsp[
        start_index:end_index
    ].strip()


import ast
import re
import json

def convert_function_call_to_json(string):
    try:
        tool_calls = []
        x = ast.parse(string)
        for tool in x.body:
            function_name = tool.value.func.id
            function_args = {}
            for keyword in tool.value.keywords:
                function_args[keyword.arg] = ast.literal_eval(keyword.value)
            this_one = {"name": function_name, "arguments": function_args}
            tool_calls.append(this_one)
        return tool_calls
    except Exception:
        return []
import json

def extract_code_from_arguments(arguments_str):
    try:
        arguments_dict = json.loads(arguments_str)
        return arguments_dict.get("code", "")
    except json.JSONDecodeError:
        return ""

def fc2dict(sequence: str, spliter="<|tool_call|>"):
    if spliter in sequence:
        content, tool_call_string = sequence.split(spliter, 1)
        try:
            # 找到第一个 { 和最后一个 }
            start_idx = tool_call_string.find('{')
            end_idx = tool_call_string.rfind('}')
            if start_idx != -1 and end_idx != -1:
                arguments_str = tool_call_string[start_idx:end_idx + 1]
                print("Arg:",arguments_str)
                arguments_str=arguments_str.replace("\n","\\n")
                #code_content = extract_code_from_arguments(arguments_str)
                tool_call_dict = {
                    "name": "execute_python",
                    "arguments": json.loads(arguments_str)
                }
                tool_calls = [tool_call_dict]
            else:
                tool_calls = []
            return {
                "content": content.strip(),
                "tool_calls": tool_calls,
                "role": "assistant",
            }
        except Exception as e:
            print(f"Error: {e}")
            return {"content": content.strip(), "role": "assistant"}
    else:
        return {"content": sequence.strip(), "role": "assistant"}

# 示例用法
sequence = '''To fulfill your request, I will perform the following steps:

1. Read the dataset from the provided path.
2. Extract the necessary data for the radar chart.
3. Create a radar chart using the extracted data.

Let's start by reading the dataset.

Action:


<|tool_call|>execute_python({"code":"import pandas as pd\n\n# Read the dataset\ndata_path = './data/radar.csv'\ndf = pd.read_csv(data_path)\ndf.head()"})\n'''
result = fc2dict(sequence)
print(result)
