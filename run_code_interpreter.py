import json
import os
import traceback

import fire
import matplotlib
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from loguru import logger
from yaml import safe_load

from llms import build_llm
from llms.utils import message2dict
from utils.output_parser import parse_code_action
from utils.save_notebook import generate_notebook, save_as_ipynb
import time

matplotlib.use("Agg")


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
    os.makedirs("cells", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    logger.info("started")
    config = safe_load(open(config_path, "r"))
    logger.info("config loaded")
    llm = build_llm(config["llm"]["type"], config["llm"]["args"])
    logger.info("llm built")
    system_prompt_template = config["system_prompt_template"]
    max_turns = config["max_turns"]
    test_data = json.load(open(task_path, "r"))
    logger.info(f"total tasks: {len(test_data)}")
    if os.path.exists(output_path):
        processed_ids = set(
            [json.loads(line)["index"] for line in open(output_path, "r")]
        )
    else:
        processed_ids = set()
    fout = open(output_path, "a")
    for task in test_data:
        tool = PythonAstREPLTool()
        file_path = ",".join(task["file_paths"])
        user_query = task["user"]
        index = task["index"]
        if index in processed_ids:
            continue
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
        cells = [
            {"role": "system", "text": system_prompt_template},
            # {"role": "system", "content": system_prompt_template.format(index=index)},
            {
                "role": "user",
                "text": "[INFO]The data is uploaded to {file_path}".format(
                    file_path=file_path
                ),
            },
            {
                "role": "user",
                "text": user_query,
            },
        ]
        for count in range(max_turns):  # max 5 turn interaction
            logger.info("--" * 10 + f"Round: {count}" + "--" * 10)
            logger.info(f"input messages: {messages}")
            out_msg, debug_info = llm.generate(messages)
            time.sleep(1)
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
            if code_script is None or code_script.strip() == "":
                messages.append({"role": "assistant", "content": reasoning})
                cells.append({"role": "assistant", "text": reasoning})
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"{reasoning}\n{config['code_start_token']}\n{code_script}\n{config['code_end_token']}",
                    }
                )
                cells.append({"role": "assistant", "text": reasoning})

            if code_script is None or code_script.strip() == "":
                break

            code_response = execute_code(code_script, tool)
            logger.info(f"Code response:\n{code_response}")
            if config["mode"] == "prompt":
                messages.append({"role": "user", "content": code_response})
                cells.append(
                    {
                        "role": "assistant",
                        "code": code_script,
                        "result": code_response,
                    }
                )
            else:
                messages.append({"role": "tool", "content": code_response})

        save_as_ipynb(generate_notebook(cells), f"cells/{index}.ipynb")
        item = {"messages": messages}
        item.update(task)
        print(json.dumps(item, ensure_ascii=False), file=fout)
    logger.info("finished")


if __name__ == "__main__":
    fire.Fire(main)
