import json
import os
import traceback

import fire
import matplotlib
#from langchain_experimental.tools.python.tool import PythonAstREPLTool
from loguru import logger
from yaml import safe_load

from llms import build_llm
from llms.utils import message2dict
from utils.assistant import GPT
from utils.output_parser import parse_code_action
from utils.save_notebook import generate_notebook, save_as_ipynb

matplotlib.use("Agg")
import nbformat
from nbclient import NotebookClient
import traceback
import time
import ruamel.yaml

def execute_code(code_str: str, Kernel, nb):
    nb.cells.append(nbformat.v4.new_code_cell(code_str))
    total_cells = len(nb.cells)
    cell = nb.cells[-1]
    client = NotebookClient(nb, allow_errors=True)
    client.kc = Kernel
    print(cell)

    try:
        client.reset_execution_trackers()
        client.execute_cell(cell=cell, cell_index=-1)
    except Exception as e:
        traceback.print_exc()
        error_message = str(e)
        return error_message

    outputs = nb.cells[-1]['outputs']

    result = ""
    for output in outputs:
        if output.output_type == "stream":  # 如果输出是标准输出或标准错误
            result += output.text
        elif output.output_type == "execute_result":  # 如果输出是执行结果
            result += str(output['data']['text/plain'])
        elif output.output_type == "error":  # 如果输出是错误
            result += "There are some errors in the code. All variables in this cell should be redefined. Please Debug:\n"
            result += "Error: " + str(output.ename) + "\n"
            result += str(output.evalue) + "\n"

    return result


import os
import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
import fire
from ruamel.yaml import safe_load
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbclient import NotebookClient
import logging

logger = logging.getLogger(__name__)

# 全局线程锁
lock = threading.Lock()

def process_task(task, config, llm, system_prompt_template, max_turns, output_path, processed_ids):
    index = task["index"]
    cell_path="Cells"
    if index in processed_ids:
        return

    file_path = ",".join(task["file_paths"])
    user_query = task["user"]

    nb = nbformat.v4.new_notebook()
    client = NotebookClient(nb, allow_errors=True)
    client.km = client.create_kernel_manager()
    client.start_new_kernel()
    client.start_new_kernel_client()
    Kernel = client.kc

    logger.info("==" * 80)
    logger.info(f"Task index: {index}")
    logger.info(f"Task:\n{user_query}")
    logger.info(f"File path: {file_path}")

    messages = [
        {"role": "system", "content": system_prompt_template},
        {"role": "user", "content": f"[INFO]The data is uploaded to {file_path}"},
        {"role": "user", "content": user_query},
    ]
    cells = [
        {"role": "system", "text": system_prompt_template},
        {"role": "user", "text": f"[INFO]The data is uploaded to {file_path}"},
        {"role": "user", "text": user_query},
    ]

    try:
        for count in range(max_turns):  # max 5 turn interaction
            logger.info("--" * 10 + f"Round: {count}" + "--" * 10)
            #logger.info(f"input messages: {messages}")
            try:
                out_msg, debug_info = llm.generate(messages)
            except:
                break
            #logger.info(f"output msg: {message2dict(out_msg)}")

            reasoning, code_script = parse_code_action(
                out_msg.content,
                mode=config["mode"],
                code_start_token=config["code_start_token"],
                code_end_token=config["code_end_token"],
                tool_call_token=config["tool_call_token"],
            )
            #logger.info(f"Reasoning: {reasoning}")
            #logger.info(f"Code script: {code_script}")
            if code_script is None or code_script.strip() == "":
                messages.append({"role": "assistant", "content": reasoning})
                cells.append({"role": "assistant", "text": reasoning})
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": out_msg.content,
                    }
                )
                cells.append({"role": "assistant", "text": reasoning})

            if code_script is None or code_script.strip() == "":
                break

            code_response = execute_code(code_script, Kernel, nb)
            #logger.info(f"Code response:\n{code_response}")
            messages.append({"role": "user", "content": "[INFO]This is a Code Interpreter Message:\n" + code_response})
            cells.append(
                {
                    "role": "assistant",
                    "code": code_script,
                    "result": code_response,
                }
            )

        save_as_ipynb(generate_notebook(cells), f"{cell_path}/{index}.ipynb")
        item = {"messages": messages}
        item.update(task)
    except Exception:
        logger.error(traceback.format_exc())
        save_as_ipynb(generate_notebook(cells), f"{cell_path}/{index}.ipynb")
        item = {"messages": messages}
        item.update(task)
    finally:
        client._cleanup_kernel()

    
    with open(output_path, 'a') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print("======Write Json=======")

def main(config_path: str, task_path: str, output_path: str):
    os.makedirs("Check", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    logger.info("started")
    yaml = ruamel.yaml.YAML()
    config=yaml.load(open(config_path, "r"))
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

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [
            executor.submit(process_task, task, config, llm, system_prompt_template, max_turns, output_path, processed_ids)
            for task in test_data
        ]
        for future in futures:
            future.result()  # 等待所有任务完成

    logger.info("finished")

if __name__ == "__main__":
    fire.Fire(main)
