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
            return rsp["content"], rsp["tool_calls"][0]["function"]["arguments"][
                "query"
            ]
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

    return rsp[:start_index].strip(), rsp[start_index:end_index].strip()


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
    except Exception:
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
