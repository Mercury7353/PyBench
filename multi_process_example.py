      
from llmcenter import ChatClient
from nbclient import NotebookClient
import nbformat
import json
import os
import re
import threading
from exact_query import QueryGenerator
from yaml import safe_load
from concurrent.futures import ThreadPoolExecutor
from utils.logger import Logger
from tqdm import tqdm
import time
import subprocess

# defines
system_prompt = """You are an AI Agent who is proficient in solve complicated task. Each step, you could reconsider the Plan(which should no more than 5 steps), generate specific Todo for current step and write code.
Each subtask in the plan should be a task need to be complete by code. You are equipped with a codeinterpreter. You can call it in the following format, then you will get the result of your code.
```python
<Your python code>
```

Each round, your answer should ALWAYS use the following format:

Analyse: Analyse the user input or the result of your executed code
This Step Todo: (The subtask you need to complete at current step, it could be fix the bug or execute the plan)
Action:(The action to complete Todo)
```python
<Your python code>
```


You will got the result of your code after each step. When the code of previous subtask is executed successfully, you can write and excuet the code for next subtask
When you complete all subtasks(completely fulfill the user query), you should summarize the previous analyse process and make a formal response to user, The response should follow this format:

Finished: <Answer to user query>


Some notice: 
1. When you want to draw a plot, use plt.save() and print the image path in markdown format instead of plt.show()
2. Your code should have proper output, responsing to user's query.
3. The variable in your past code can be used directly in new code snippt.
4. Try to solve the problem step by step with short code. You can get more information from the results of running the code in the middle.
5. End the process when you complete the task, When you do not have Action(Code), Use: Finished: <summary the analyse process and make response>
"""

# conf area
conf = safe_load(open("./config/my_conf.yaml", "r"))
config_dict = conf["llm"]["args"]

user_token, app_code = config_dict["user_token"], config_dict["app_code"]
model_id = config_dict["model_id"]

# 全局变量
bad_count = 0 # 记录失败次数
success_count = 0 # 记录成功次数
lock = threading.Lock()

# 变量
gap, worker = 180, 5
dir_name = "0624_v1_csv"
data_dir = "csv_data"
qg = QueryGenerator(user_token=user_token, app_code=app_code, model_id=model_id)

def execute_code_v2(code_str, kernel, nb, logger):
    
    # 添加一个包含代码的cell
    nb.cells.append(nbformat.v4.new_code_cell(code_str))
    
    cell = nb.cells[-1]
    
    client = NotebookClient(nb, allow_errors=True)
    client.kc = kernel
    
    
    try:
        client.reset_execution_trackers()
        client.execute_cell(cell=cell,cell_index=-1)
    except Exception as e:
        logger.warning(f"execute bad, error is {e}")
        error_message = nb.cells[-1]['outputs'][0]['evalue']
        return f"Error: {error_message}"
    
    # 提取执行结果
    try:
        outputs = nb.cells[-1]['outputs']#[0]['data']['text/plain'])
        assert len(outputs) > 0

        result = ""
        for output in outputs:
            if output.output_type == "stream":  # 如果输出是标准输出或标准错误
                result += output['text']
            elif output.output_type == "execute_result":  # 如果输出是执行结果
                result += str(output['data']['text/plain'])
            elif output.output_type == "error":
                result += str(output['evalue'])
    except:
        print(f"warning! get result error, output is {outputs}")
        logger.error(f"get result error, output is {outputs}")
        return "execute code error!!"

    return result



def execute_code(code_str, nb, logger):
    # 添加一个包含代码的cell
    nb.cells.append(nbformat.v4.new_code_cell(code_str))

    # 执行notebook
    client = NotebookClient(nb)
    try:
        client.execute()
    except Exception as e:
        logger.warning(f"execute bad, error is {e}")
        error_message = nb.cells[-1]['outputs'][0]['evalue']
        return f"Error: {error_message}"
    
    # 提取执行结果
    try:
        outputs = nb.cells[-1]['outputs']#[0]['data']['text/plain'])

        result = ""
        for output in outputs:
            if output.output_type == "stream":  # 如果输出是标准输出或标准错误
                result += output['text']
            elif output.output_type == "execute_result":  # 如果输出是执行结果
                result += str(output['data']['text/plain'])
    except:
        print(f"warning! get result error, output is {outputs}")
        logger.error(f"get result error, output is {outputs}")
        return "execute code error!!"

    return result

def extract_code(text):
    pattern = r'```python(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    # 如果没有找到或找到多个，则设置 code 为空
    if len(matches) != 1:
        return ""
    
    return matches[0].strip()


def roll_back(nb):
    nb.cells.pop()
    return nb


def process_file(start_index, end_index):

    global bad_count, success_count

    logger = Logger(f"/home/jeeves/waple/DataGen/logs/{dir_name}/{start_index}-{end_index}_record.log")
    chat_client = ChatClient(app_code=app_code, user_token=user_token, model_id=model_id)
    write_path = f'/home/jeeves/waple/DataGen/output/{dir_name}/{start_index}-{end_index}.jsonl'
    data_total_dir = f'/home/jeeves/waple/DataGen/data/{data_dir}/'

    # build notebook client
    nb = nbformat.v4.new_notebook()
    client = NotebookClient(nb, allow_errors=True)
    client.km = client.create_kernel_manager()
    client.start_new_kernel()
    client.start_new_kernel_client()
    kernel = client.kc

    for i, file_name in tqdm(enumerate(os.listdir(data_total_dir)[start_index:end_index]), ascii=True, desc=f"{start_index}~{end_index}", total=gap):
    
        file_path = f'/home/jeeves/waple/DataGen/data/{data_dir}/{file_name}'.format()
        file_index = i + start_index
        try:
            # check file suffix
            if not (file_name.endswith(".csv") or file_name.endswith(".xlsx") or file_name.endswith(".xls") or file_name.endswith(".txt") or file_name.endswith(".pdf")):
                logger.warning(f"{file_index} file type is bad, which is {file_name}")
                continue
            logger.info("\n**********************************************************\n")
            logger.info(f"\nfile index {file_index} \n[Thread {start_index}-{end_index}]\nRead file:{file_name}\n")

            # build user instruction
            user_instruction = qg.generate_query(file_path)

            # init return messages
            full_messages = [
                {
                    "role": "user",
                    "content": f"I have uploaded the file to this path:{file_path}"
                },
                {
                    "role": "user",
                    "content": user_instruction,
                }
            ]

            # chat loop
            success = 0
            for index in range(10):
                # sleep 1s before request
                time.sleep(1)
                try:
                    resp = chat_client.chat_sync(system_prompt=system_prompt, messages=full_messages)
                except Exception as e:
                    # cold down and retry
                    logger.warning(f"\nloop {index} sleep 30s\n")
                    print(f"llmcenter error: {e}\nlet's sleep 30s")
                    time.sleep(30)
                    continue
                logger.info(f"\nloop index {index}'s response is: {resp}\n")

                if "Finished" in resp:
                    full_messages.append({
                        "role": "ai",
                        "content": resp
                    })
                    success = 1
                    logger.info(f"\ngeneration is done, cost {index} loop")
                    break

                code = extract_code(resp)
                if code == "":
                    logger.warning("\ncode is empty, try to regenerate...\n")
                    continue

                #code_result = execute_code(code, nb, logger)
                code_result = execute_code_v2(code, kernel, nb, logger)
                logger.info(f"\nexecute result: \n{code_result}")

                if "Error" in code_result:
                    roll_back(nb)

                # add to messages
                full_messages.append({
                    "role": "assistant",
                    "content": resp
                })
                full_messages.append({
                    "role": "user",
                    "content": f"[INFO]This is a codeinteroreter message: The code result is {code_result}"
                })

            with lock:
                if not success:
                    bad_count += 1
                    print(f"bad count++\nnow success/bad is: {success_count}/{bad_count}")
                    logger.warning("\nthis data is bad... drop it\n")
                    continue
                # else success
                success_count += 1
                logger.info(f"\n\n<step>{index+1}</step>\n\n")
            
            # view success count
            if success_count % 20 == 0:
                print(f"now success/bad is: {success_count}/{bad_count}")

            # add records to file
            with open(write_path, "a") as f:
                json_string = json.dumps(full_messages, ensure_ascii=False)
                f.write(json_string + "\n")
                logger.info(f"\nindex {file_index} successfully add to jsonl\n")
        
        except Exception as e:
            logger.error(f"get exception index {file_index}, error {e}, reset nb")
            nb = nbformat.v4.new_notebook()
            assert ValueError(f"e")
        
        logger.info("\n**********************************************************\n\n")

if __name__ == "__main__":

    # make log/output json dir if not exist
    if not os.path.exists(log_dir := f"/home/jeeves/waple/DataGen/logs/{dir_name}"):
        os.mkdir(log_dir)
    if not os.path.exists(output_dir := f"/home/jeeves/waple/DataGen/output/{dir_name}"):
        os.mkdir(output_dir)

    # launch multi-thread
    with ThreadPoolExecutor(max_workers=worker) as executor:
        for i in range(worker):
            start_index, end_index = i * gap, (i + 1) * gap 
            executor.submit(process_file, start_index, end_index)

    