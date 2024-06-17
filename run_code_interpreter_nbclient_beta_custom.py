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
from utils.assistant import GPT
from utils.output_parser import parse_code_action
from utils.save_notebook import generate_notebook, save_as_ipynb
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from langchain_community.llms import VLLM


matplotlib.use("Agg")
os.environ["AZURE_OPENAI_API_KEY"] = "b5ceeca154844f009e4d6618188305d3"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://zyl-code-interpreter.openai.azure.com/"

import nbformat
from nbclient import NotebookClient
def execute_code(code_str: str,Kernel,nb):
    #print("codeSTr",code_str)
    # 创建一个新的notebook对象
    #code_str = code_str.replace('\\n', '\n')
    
    # 添加一个包含代码的cell
    nb.cells.append(nbformat.v4.new_code_cell(code_str))
    
    total_cells=len(nb.cells)
    #print(total_cells)
    cell = nb.cells[-1]
    
    #nb_new=nbformat.v4.new_notebook()
    # 执行notebook
    
    client = NotebookClient(nb,allow_errors=True)
    client.kc=Kernel
    
    #client.execute()

    
    print(cell)
    #print("Name",client.kc)
    #outputs=nb.cells[-1]['outputs']#[0]['data']['text/plain']
    #print("Output",outputs)
    
    try:
        client.reset_execution_trackers()
        client.execute_cell(cell=cell,cell_index=-1)
    except Exception as e:
        #print("Code error")
        traceback.print_exc()
        
        #error_message=traceback.format_exc()
        error_message=str(e)
        #split('Traceback')[-2]
        #error_message=error_message.split("\n")[-2]
        #print("Error",error_message)
        return error_message
    #"There are some errors in the code. All variable in this cell should be redefined,Please Debug:\n"+error_message
    
    # 提取执行结果
    #outputs = nb.cells[-1].outputs
    #print("CheckOutput",nb_c.cells[-1]['outputs'][0])
    outputs=nb.cells[-1]['outputs']#[0]['data']['text/plain']
    #print("Output",outputs)
    
    result = ""
    for output in outputs:
        #print("check point:",output.output_type)
        if output.output_type == "stream":  # 如果输出是标准输出或标准错误
            result += output.text
        elif output.output_type == "execute_result":  # 如果输出是执行结果
            result += str(output['data']['text/plain'])
        elif output.output_type == "error":  # 如果输出是错误
            result += "There are some errors in the code. All variable in this cell should be redefined,Please Debug:\n"
            result += "Error: " + str(output.ename) + "\n"
            result += str(output.evalue) + "\n"
            #result += "".join(output.traceback) + "\n"
            #roll_back(nb)
    #print(result)
    return result

def _execute_code(code_str: str, tool: PythonAstREPLTool):
    """execute python code and return the execution result

    Args:
        code_str (str): the code to be executed
        tool (PythonAstREPLTool): python ast repl tool

    Returns:
        str: code execution result
    """
    # TODO: PythonAstREPLTool do not return full traceback when error occurs
    try:
        result = tool.invoke(code_str)
        result = str(result)
        return result
    except:
        return traceback.format_exc()


def main(config_path: str, task_path: str, output_path: str):
    os.makedirs("OpenCodeInterpreter_DS_7b_Cells", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    logger.info("started")
    config = safe_load(open(config_path, "r"))
    logger.info("config loaded")
    #llm = build_llm(config["llm"]["type"], config["llm"]["args"])
    stop_token_ids = [151329, 151336, 151338]
    sampling_params = SamplingParams(temperature=0.95, max_tokens=1024, stop_token_ids=stop_token_ids)
    model_path="/data/zyl7353/models/OpenCodeInterpreter-DS-6.7B"
    llm = LLM(
    model=model_path,
    tensor_parallel_size=1,
    trust_remote_code=True,
    enforce_eager=True,
    # GLM-4-9B-Chat-1M 如果遇见 OOM 现象，建议开启下述参数
    # enable_chunked_prefill=True,
    # max_num_batched_tokens=8192
)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    logger.info("llm built")
    system_prompt_template = config["system_prompt_template"]
    max_turns = config["max_turns"]
    test_data = json.load(open(task_path, "r"))
    logger.info(f"total tasks: {len(test_data)}")
    if os.path.exists(output_path):
        processed_ids = set(
            [json.loads(line)["index"] for line in open(output_path, "r")]
        )
        #print("Processed")
        #processed_ids={str(i) for i in range(152)}
        #print(processed_ids)
    else:
        processed_ids = set()
    fout = open(output_path, "a")
    for task in test_data:
        if config["mode"] == "assistant":
            file_path = task["file_paths"]
            user_query = task["user"]
            index = task["index"]
            My_Assistant = GPT(output_path)

            My_Assistant.chat(user_query, file_path, index)
            continue
        file_path = ",".join(task["file_paths"])
        user_query = task["user"]
        index = task["index"]
        if index in processed_ids:
            continue
        nb=nbformat.v4.new_notebook()
        client = NotebookClient(nb,allow_errors=True)
        client.km=client.create_kernel_manager()
        print("Has kernel",client.km.has_kernel)
        client.start_new_kernel()
        print("Has kernel",client.km.has_kernel)
        client.start_new_kernel_client()
        Kernel=client.kc
        
        logger.info("==" * 80)
        logger.info(f"Task index: {index}")
        logger.info(f"Task:\n{user_query}")
        logger.info(f"File path: {file_path}")

        messages = [
            #{"role": "system", "content": "你是一个名为 GLM-4 的人工智能助手。你是基于智谱AI训练的语言模型 GLM-4 模型开发的，你的任务是针对用户的问题和要求提供适当的答复和支持。"},
            {"role": "system", "content": system_prompt_template.format(index=index)},
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
            #{"role": "system", "text": "你是一个名为 GLM-4 的人工智能助手。你是基于智谱AI训练的语言模型 GLM-4 模型开发的，你的任务是针对用户的问题和要求提供适当的答复和支持。"},
             {"role": "system", "content": system_prompt_template.format(index=index)},
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
        try:
            for count in range(max_turns):  # max 5 turn interaction
                logger.info("--" * 10 + f"Round: {count}" + "--" * 10)
                logger.info(f"input messages: {messages}")
                input_messages=tokenizer.apply_chat_template(messages, add_generation_prompt=True,
                                       tokenize=False,
                                       return_tensors="pt",
                                       return_dict=False)
                out_msg = llm.generate(input_messages,sampling_params)
                #print(out_msg)
                generated_text = [output.outputs[0].text for output in out_msg]
                #logger.info(f"output msg: {message2dict(out_msg)}")

                reasoning=generated_text[0].split("python\n")[0]
                try:
                    code_script =generated_text[0].split("python\n")[1]
                    if "```" in code_script:
                        code_script=code_script.split("```")[0]
                except:
                    code_script=None
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

                code_response = execute_code(code_script, Kernel,nb)
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

            #save_as_ipynb(generate_notebook(cells), f"OpenCodeInterpreter_DS_7b_Cells/{index}.ipynb")
            item = {"messages": messages}
            item.update(task)
            #print(json.dumps(item, ensure_ascii=False), file=fout)
        except Exception:
            logger.error(traceback.format_exc())
            #save_as_ipynb(generate_notebook(cells), f"OpenCodeInterpreter_DS_7b_Cells/{index}.ipynb")
            item = {"messages": messages}
            item.update(task)
            #print(json.dumps(item, ensure_ascii=False), file=fout)
        client._cleanup_kernel()
        with open(output_path,'a') as f:
            f.write(json.dumps(item, ensure_ascii=False)+'\n')
            print("======Write Json=======")

    logger.info("finished")


if __name__ == "__main__":
    fire.Fire(main)
