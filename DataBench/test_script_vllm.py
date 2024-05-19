'''
This file aims to generate strong sft data, to help llama3-8b learn the ability to debug. (Learn from gpt-3.5-turbo)
Step 1. Start vllm
Step 2. Load query (random/select)
Step 3. Run the query
Step 4. Detect Bug
Step 5. Use GPT-3.5 fix bug
0506:再写一个redebug message，用function call的形式维护一个消息队列
0508:直接调旧版的llm center,
```python
<code>
```
形式输出代码
当change to GPT时，替换一下system prompt,
if LLM.name=="GPT":
    import DataGen里面的老函数


'''
import sys
sys.path.append("..")
#sys.path.append("/home/jeeves/zyl/zyl7353/CodeInterpreter/ReAct/ReAct/redebug")
from os import system
#from exact_query import generate_exact_query
import os
import openai
from llama3 import LlaMa3
#from DataGen import system_prompt_template
from typing import Dict, List, Optional, Tuple, Union
#from GPT import GPT

#from llmcenter import ChatClient
import re
import requests
import os, sys
import json
import traceback
import time
import random
from tqdm import tqdm
import pdb
from copy import deepcopy
from langchain_experimental.tools.python.tool import PythonAstREPLTool


def execute_code(code_str: str, tool: PythonAstREPLTool):
    try:
        result = tool.invoke(code_str)
        result = str(result)
        return result
    except:
        return traceback.format_exc()


def _execute_code(code_str: str):
    from nbclient import NotebookClient
    import nbformat
    #print("codeSTr",code_str)
    # 创建一个新的notebook对象
    code_str = code_str.replace('\\n', '\n')

    # 添加一个包含代码的cell
    nb.cells.append(nbformat.v4.new_code_cell(code_str))

    total_cells=len(nb.cells)

    # 执行notebook
    client = NotebookClient(nb)
    try:
        client.execute()
    except Exception as e:
        #print("Code error")

        #error_message=traceback.format_exc()
        error_message=str(e)
        #split('Traceback')[-2]
        #print(error_message)
        #()
        return error_message

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
            result += "Error: " + str(output.ename) + "\n"
            result += str(output.evalue) + "\n"
            result += "".join(output.traceback) + "\n"
    #print(result)
    return result
def roll_back():
    nb.cells.pop()
    return nb
def startVLLM():
    system("bash /data/zyl7353/CodeInterpreter/ObjLLaMa/vllm/examples/initialChat.sh")
    return

def extract_code(rsp):
    #extract code to excute from rsp
    rsp=str(rsp)


        # 正则表达式
    #print("CheckRSP",rsp)
    # 正则表达式
    pattern = r'excute_python\(code=(["\'])(.*?)\1\)'
    # 定义正则表达式
    pattern = r'excute_python\(code=(["\'])([\s\S]*?)\1\)'
    # 使用re.findall查找所有匹配项
    match = re.search(pattern, rsp)
    # 打印匹配到的内容
    if match:
        #print("MATCH Check",match)
        code=match.group(2)
        if "\\n" in code:
            code=code.replace("\\n","\n")
            print("Format Error Fixed")
        if "```" in code:
            code=code.replace("```","")
        if "python" in code:
            code=code.replace("python","")
        if '''\\"''' in code:
            code=code.replace("\"",'"')
        if "\\'" in code:
            code=code.replace("\'","'")

        return code

    code=parse_code_argument(rsp)
    if "\\n" in code:
        code=code.replace("\\n","\n")
        print("Format Error Fixed")
    if "```" in code:
        code=code.replace("```","")
    if "python" in code:
        code=code.replace("python","")
    if "\"" in code:
        code=code.replace("\"",'"')
    if "\'" in code:
        code=code.replace("\'","'")
    return code
def _extract_code(rsp):

    try:
        code=rsp.split('```')[-2]
        code=code.replace("python","")
    except:
        code=""
    return code

def parse_code_argument(input_str):
    # 首先匹配外层的code参数
    outer_pattern = r"excute_python\(code=(\{.*?\})\)"
    match = re.search(outer_pattern, input_str, re.DOTALL)

    if not match:
        return ""

    # 尝试解析匹配到的JSON字符串
    try:
        code_arg = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        return f"JSON decode error: {str(e)}"

    # 提取并返回code键对应的值
    code_content = code_arg.get("code", None)
    return code_content



def main():

    system_prompt_template= """ You are an AI Agent who is proficient in solve complicated task. Each step, you should first think step by step according to user query and previous messages. The code you write will be appended to a notebook as a new cell. You will get the excution result of the cell
When you find you code is error, you last code is removed from the notebook, which means you should rewrite the whole cell(redefine all variables)

Each round, your answer should ALWAYS use the following format:


Analyse:(Analyse the message you received and plan what you should do)
This Step Todo: One Subtask need to be done at this step
Action:(The action to complete Todo,)
```python
<your code>
```

You will got the result of your code after each step. When the code of previous subtask is excuted successfully, you can write and excuet the code for next subtask
When all the code your write are executed and you got the code result that can fulfill the user query, you should summarize the previous analyse process and make a formal response to user, The response should follow this format:
WARNING:MAKE SURE YOU GET THE CODE EXECUTED RESULT THAT FULFILLED ALL REQUIREMENT OF USER BEFORE USE "Finished"
Finished: <Answer to user query>


Some notice:
1. When you want to draw a plot, use plt.save() and print the image path in markdown format instead of plt.show()
2. Save anything to ./output folder, make sure the index: {index} is included in your file name
3. End the process whenever you complete the task, When you do not have Action(Code), Use: Finished: <summary the analyse process and make response>

"""


    #system_prompt_template
    #startVLLM() # 会占用当前bash，需要另外单独启动


    LLM=LlaMa3(tools=None)
    with open("task.json") as f:
        json_str=f.read()
        print(json_str)
        test_data=json.loads(json_str)
    #print(test_data)

    for task in test_data:
        tool = PythonAstREPLTool()
        print("Task:\n",task['user'])
        turns=[]
        #print(task.keys())
        file_path=task['file_path']
        user_query=task['user']
        index=task['index']
        # 清空所有单元
        #nb.cells = []

        code_result=execute_code('''import os
current_path = os.getcwd()
print("当前执行路径是:", current_path)''', tool)
        print(code_result)
        messages=[
            {"role":"system","content":system_prompt_template.format(index=index)},
            {'role':"user","content":"[INFO]The data is uploaded to {file_path}".format(file_path=file_path)},
            {"role":"user","content":"Use uploaded data to fulfill the requirement:\n"+user_query}
        ]
        count=0
        for _ in range(10): #max 5 turn interaction
            count+=1
            print("Round:",count)
            if LLM.name=="Llama3":
                try:
                    rsp=LLM.chat(messages)
                except:
                    break
                print("LLama3 response\n",rsp)
            #if LLM.name=="LLama3":
            messages.append({"role":"assistant","content":rsp})


            if "Finished" in rsp:
                break
            #if LLM.name=="GPT":
            code=_extract_code(rsp)
            #else:
            #    code=_extract_code(rsp)

            #print("Response:\n",rsp)
            #print("Code:\n",code)

            code_result = execute_code(code, tool)


            if "Error" in code_result:
                messages.append({"role":"user","content":"This is the execution result of your code: "+code_result})
                print("Code Result:\n",code_result)
                continue
                roll_back()
                error_message=code_result.split('\n')[-2]
                print("Code Result\n",error_message)
                messages.append({"role":"user","content":"This is the execution result of your code: "+error_message})
                continue
                #print("Debug",messages[-2:])
                #debug_msg=Message(role=RoleType.USER,content="You are a code reviewer, please repeat the bug first and analyse why the code has the bug, just return your reasoning process,do not return any code.Please also Check This:When the code want to draw a plot, use plt.savefig() and print the image path in markdown format instead of plt.show()")
                #debug_messages=funcall_messages[-2:]
                #debug_messages.append(debug_msg)
                #debugger_info=debugger.chat(messages=debug_messages,tools=None)[0].content
                #funcall_messages.append(Message(role=RoleType.USER,content=debugger_info+"Now, Please fix the bug complete the rest part of the task"))
                #print("Debug Info\n",debugger_info)
                #messages.append({"role":"user","content":debugger_info+"Now, Please fix the bug and excute the code"})
            else:
                messages.append({"role":"user","content":"This is the execution result of your code: "+code_result})
                print("Code Result:\n",code_result)


            #messages.append({"role":"tool","content":code_result})
            #print("Code Result:\n",code_result)

        #json_file_name = './trajectory_qwen_chat_0518.jsonl'
        json_file_name = './trajectory_qwen_ours_0518.jsonl'

        # 使用 json.dump 方法将字典列表写入 JSON 文件
        with open(json_file_name, 'a') as wr:
            json_string=json.dumps(messages,ensure_ascii=False)
            #wr.write(json_string+'\n')
            print("write jsonl")


if __name__ =="__main__":
    #nb = nbformat.v4.new_notebook()# A Global notebook
    print("Start")
    main()

#解析：
# excute_python(code="\\nimport pandas as pd\\nimport matplotlib.pyplot as plt\\nfrom textblob import TextBlob\\n\\n# Read in the data\\nmovies = pd.read_csv(\'100 Best Movies on Netflix_shuffled.csv\')\\n\\n# Extract the critics\' consensus for each movie\\nconsensus = movies[\'Critics Consensus\']\\n\\n# Analyze the sentiment of the critics\' consensus\\nsentiment = [TextBlob(text).sentiment.polarity for text in consensus]\\n\\n# Generate a bar plot of the movie ratings\\nratings = movies[\'Rating\']\\nplt.bar(movies[\'Title\'], ratings)\\nplt.title(\'Movie Ratings\')\\nplt.xlabel(\'Title\')\\nplt.ylabel(\'Rating\')\\nplt.show()\\n\\n# Print the sentiment scores\\nprint(sentiment)\\n")
