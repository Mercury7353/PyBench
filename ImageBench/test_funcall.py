'''
Test gpt-3.5 ,gpt-4 on ImageBench, equipped it with a tool: excute_python

'''
import sys
#sys.path.append("/home/jeeves/zyl/zyl7353/CodeInterpreter/ReAct/ReAct")
#sys.path.append("/home/jeeves/zyl/zyl7353/CodeInterpreter/ReAct/ReAct/redebug")
sys.path.append("..")
from llmcenter import ChatClient
from nbclient import NotebookClient
#from DS_Query_Gen import Generate_task_sequence
#from DS_Query_Gen import Generate_DAG
#from Codereviewer import Codereviewer
#Input Description, output :task sequence
import nbformat
import copy
import json
import traceback
import random
import os
import jsonlines
import re
import time
from GPT import GPT
from adc import (
    DebugInfo,
    Function,
    Message,
    RoleType,
    Tool,
    ToolCall,
    ToolProperty,
)
from typing import Dict, List, Optional, Tuple, Union
# dataset, image, video
#from exact_query import generate_exact_query
# multi-turn conversation
user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)
#user =ChatClient(app_code='CodeAndFunction',user_token=user_token,model_id=20)
# 20 gpt-35-turbo
# 36 gpt-4-1106-preview

def Plan_Act(chat_history):
    #codereviewer=Codereviewer()
    #print(question)
    final_act=''
    final_Obs=''
    for i in range(3):
        try:
            msg = chat.chat_sync(system_prompt=system_prompt_template, messages=chat_history)
            print(msg)
           
            try:
                
                action = msg.split('```')[-2]
                chat_history.append({'role':"ai","content":msg})
            except:
                print("No code response")
                #print("Check Point",msg)
                #if "Finished" in msg:
                chat_history.append({'role':"ai","content":msg})
                return chat_history,"Finished"
            
            action=action.replace("python",'')
          
            CodeResult=execute_code(action)
            print("CodeResult",CodeResult)
            if "Error" in CodeResult:
                chat_history.append({"role":"user","content":"Observation:There are some bugs in the code, please debug:\n{CodeResult}".format(CodeResult=CodeResult)})   
                return chat_history,""  
            else:

                return chat_history,"Finished" 
            #print(full_messages)
            #CodePassport,CodeSuggestion=codereviewer.check(question=question,code=action,CodeResult=CodeResult)
           
                
                        

        


            
            

        except Exception as e:
            #messages=messages[0:-1]
            #raise e
            #print(e)
            traceback.print_exc()
            
            print("format error: Retry request")
            continue
def message_convert(messages: List[Message]):
    new_messages = []
    for msg in messages:
            new_msg = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.role.value == "assistant" and msg.tool_calls is not None:
                new_msg["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in msg.tool_calls
                ]
            if msg.role.value=="tool":
                new_msg["tool_call_id"]=msg.tool_call_id
            new_messages.append(new_msg)
    return new_messages
def execute_code(code_str: str):
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
        print("CheckError Message",error_message)
        roll_back()
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
            print("ErrorResult",result)
    return result
def roll_back():
    nb.cells.pop()
    return nb
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
        if "\"" in code:
            code=code.replace("\"",'"')
        if "\'" in code:
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

system_prompt_template = """You are an AI Agent who is proficient in processing image  through opencv or another packages. 
You are equipped with a codeinterpreter, you can run the code and get the result by calling the excute_python function
Each round, you are going to get a user query. The user is a newbie in writing python code. 
So you must tell the user the reasoning process when you write your code.
You should excute it and generate new images to fulfill user query


Notice:
1. You should always output a image througn plt.savefig instead of plt.show, You should save the processed image at :/home/jeeves/zyl/zyl7353/CodeInterpreter/Benchmark/ourbench/ImageBench/output4/{index}.png
"""
if __name__=="__main__":
    with open("task.json") as f:
        json_str=f.read()
        test_data=json.loads(json_str)
    #print(test_data)
    failed_task=0.0
    pass_task=0.0
    turn_list=[]
    tools= [
      {
        "name": "excute_python",
        "description": "excute the python code and get result, in the beginning of your code, you must write few lines of comment telling why you write this code",
        "parameters": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "The code is going to be excuted"
            },
          },
          "required": [
              "code"
          ]
        }
      }
    ]
    for task in test_data:
        
        print("Task:\n",task['user'])
        #print(task.keys())
        file_path=task['file_path']
        user_query=task['user']
        index=task['index']
        funcall_messages=[]
        funcall_msg=Message(role=RoleType.SYSTEM,content=system_prompt_template)
        funcall_messages.append(funcall_msg)
        funcall_msg=Message(role=RoleType.USER,content="[INFO]The {index}th image is uploaded to {file_path}".format(index=index,file_path=file_path))
        funcall_messages.append(funcall_msg)
        funcall_msg=Message(role=RoleType.USER,content=user_query)
        funcall_messages.append(funcall_msg)
        #funcall_messages=[Message(RoleType.SYSTEM,content=system_prompt_template),Message(role=RoleType.USER,content="[INFO]The file is uploaded to {file_path}".format(file_path=file_path)),Message(role=RoleType.USER,content=query)]
        
        LLM=GPT(model="gpt-35-turbo-0613",temperature=0.2)
        
        flag=0#Whether success
        nb = nbformat.v4.new_notebook()# A Global notebook
        #messages=[{"role":"system","content":system_prompt_template.format(index=index)},{'role':"user","content":"[INFO]The {index}th image is uploaded to {file_path}".format(index=index,file_path=file_path)},{"role":"user","content":user_query}]
        for _ in range(3):
            rsp=LLM.chat(messages=funcall_messages,tools=tools)
            print(rsp)
            for t in range(1):
                break
                if len(rsp[0].content)==0:
                    time.sleep(3)
                    rsp=LLM.chat(messages=funcall_messages,tools=tools)
                    print(rsp)

                else:
                    break
            content=rsp[0].content
            rsp=rsp[0]
            print("GPT-response:\n",content)
            #print(rsp.tool_calls[0])
            #print(rsp.tool_calls[0].function)
            #print(rsp.tool_calls[0].function.arguments)
            try:
                code=eval(rsp.tool_calls[0].function.arguments)['code']
            except:
                print("Failed Task")
                turn_list.append(3)
                break
            print("Code:\n",code)
            code_result = execute_code(code)
            if "error" in code_result:
                current_tool_call_id=str(_)

                funcall_msg=rsp
                funcall_messages.append(funcall_msg)
                current_tool_call_id=rsp.tool_call_id
                funcall_messages.append(Message(role=RoleType.TOOL,content=code_result))
                #roll_back()
            else:
                print("Task Complete!")
                pass_task+=1
                flag=1
                turn_list.append(_+1)
                break
        if flag==1:
            messages=message_convert(funcall_messages)
        else:
            turn_list.append(3)
            messages=[{"role":"system","content":"Task Failed"}]
        with open("./gpt4_funcall.jsonl",'a') as f:
            json_string=json.dumps(messages,ensure_ascii=False)
            f.write(json_string+'\n')
            print("write jsonl")
 
        



    print("PassCount:",pass_task)
    print("PassRate:",pass_task/len(test_data))
    print(turn_list)
    print(len(turn_list))
    print("Average Turn:",sum(turn_list)/len(turn_list))

        
        

        

