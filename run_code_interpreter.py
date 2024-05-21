import json
import traceback
from typing import Any, Dict

import fire
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from loguru import logger
from yaml import safe_load

from llms import BaseLLM, LLMCenter, OpenAIAPI
from llms.utils import message2dict
from utils.output_parser import parse_code_action


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


def execute_code(code_str: str, tool: PythonAstREPLTool):
    """execute python code and return the execution result

    Args:
        code_str (str): the code to be executed
        tool (PythonAstREPLTool): python ast repl tool

    Returns:
        str: code execution result
    """
    try:
        result = tool.invoke(code_str)
        result = str(result)
        return result
    except:
        return traceback.format_exc()


def main(config_path: str, task_path: str, output_path: str):
    logger.info("started")
    config = safe_load(open(config_path, "r"))
    logger.info("config loaded")
    llm = build_llm(config["llm"]["type"], config["llm"]["args"])
    logger.info("llm built")
    system_prompt_template = config["system_prompt_template"]
    max_turns = config["max_turns"]
    test_data = json.load(open(task_path, "r"))
    fout = open(output_path, "w")
    logger.info(f"total tasks: {len(test_data)}")
    for task in test_data:
        tool = PythonAstREPLTool()
        file_path = task["file_path"]
        user_query = task["user"]
        index = task["index"]

        logger.info("==" * 80)
        logger.info(f"Task index: {index}")
        logger.info(f"Task:\n{user_query}")
        logger.info(f"File path: {file_path}")

        messages = [
            {"role": "system", "content": system_prompt_template},
            # {"role": "system", "content": system_prompt_template.format(index=index)},
            {
                "role": "user",
                "content": "[INFO]The data is uploaded to {file_path}".format(
                    file_path=file_path
                ),
            },
            {
                "role": "user",
                "content": user_query,
            },
        ]
        for count in range(max_turns):  # max 5 turn interaction
            logger.info("--" * 10 + f"Round: {count}" + "--" * 10)
            logger.info(f"input messages: {messages}")
            out_msg, debug_info = llm.generate(messages)
            logger.info(f"output msg: {message2dict(out_msg)}")

            reasoning, code_script = parse_code_action(
                out_msg.content,
                mode=config["mode"],
                code_start_token=config["code_start_token"],
                code_end_token=config["code_end_token"],
                tool_call_token=config["tool_call_token"],
            )
            logger.info(f"Reasoning: {reasoning}")
            logger.info(f"Code script: {code_script}")
            messages.append({"role": "assistant", "content": out_msg.content})

            if code_script is None or code_script.strip() == "":
                break

            code_response = execute_code(code_script, tool)
            logger.info(f"Code response:\n{code_response}")
            if config["mode"] == "prompt":
                messages.append({"role": "user", "content": code_response})
            else:
                messages.append({"role": "tool", "content": code_response})
        print(json.dumps({"messages": messages}), file=fout)
    logger.info("finished")


if __name__ == "__main__":
    fire.Fire(main)
