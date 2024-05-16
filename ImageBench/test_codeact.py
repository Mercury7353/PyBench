'''
This file is a test script to test on our benchmark
'''
# generate codeinterpreter data
'''
This file generate image process data
'''
import sys
#sys.path.append("/home/jeeves/zyl/zyl7353/CodeInterpreter/ReAct/ReAct")
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
# dataset, image, video
#from exact_query import generate_exact_query
# multi-turn conversation
user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)
#user =ChatClient(app_code='CodeAndFunction',user_token=user_token,model_id=20)

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
  
    
system_prompt_template = """You are an AI Agent who is proficient in writing image processing code through opencv or another packages. 
Each round, you are going to get a user query. 
The user is a newbie in writing opencv code. 
So you must tell the user the reasoning process when you write your code and how the code work when it is excuted in detail and then You should return your code in the following format:
```python
<Your python code with comment each line>
```


Your answer should ALWAYS use the following format:

Reasoning: Detailed explaination of the code
Action:(The action to complete Todo)
```python
<Your python code with comment each line>
```

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
    for task in test_data:
        print("Task:\n",task['user'])
        #print(task.keys())
        
        file_path=task['file_path']
        user_query=task['user']
        index=task['index']
        
        nb = nbformat.v4.new_notebook()# A Global notebook
        messages=[{"role":"system","content":system_prompt_template.format(index=index)},{'role':"user","content":"[INFO]The {index}th image is uploaded to {file_path}".format(index=index,file_path=file_path)},{"role":"user","content":user_query}]
        for _ in range(3):
            messages,flag=Plan_Act(chat_history=messages)
            if flag =="Finished":
                turn_list.append(_+1)
                pass_task+=1.0
                break
        if flag!="Finished":
            turn_list.append(3)
        with open("./gpt4_codeact.jsonl",'a') as f:
            json_string=json.dumps(messages,ensure_ascii=False)
            f.write(json_string+'\n')
            print("write jsonl")

    print("PassCount:",pass_task)
    print("PassRate:",pass_task/len(test_data))
    print("Average Turn:",sum(turn_list)/len(turn_list))

        
        

        

