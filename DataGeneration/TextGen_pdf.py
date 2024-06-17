from llmcenter import ChatClient
from nbclient import NotebookClient
from DS_Query_Gen import Generate_task_sequence
from DS_Query_Gen import Generate_DAG
from Codereviewer import Codereviewer
#Input Description, output :task sequence
import nbformat
import copy
import json
import traceback
import random
import os
import jsonlines
# dataset, image, video
from exact_query_pdf import generate_exact_query
from llmcenter import ChatClient
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import traceback
import json
# multi-turn conversation



def load_data(input_file):
    """Read problems from a JSON file, sort by length, and save the top N longest problems."""
    query=generate_exact_query(input_file)
    return query


def execute_code(code_str: str):
    #print("codeSTr",code_str)
    # 创建一个新的notebook对象
    #code_str = code_str.replace('\\n', '\n')
    
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
    print(result)
    return result
def roll_back():
    nb.cells.pop()
    return nb


user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
#chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)
system_prompt='''
You are are helpful assistant who is good at write python code to slove complex text based problems. 
The user will upload a file to certain path. You should write code to read the content(like first few thousands words) of the file, then fulfill user's requirement
You have a sandbox environment which have access to file and can import packages
You are equipped with a python codeinterpreter, which receive your code and run your code in a sandbox environment. it will bring your the execution result of the code.
You can call the python codeinterpreter in the following format, make sure your code is executable and will give you correct answer :

```python
<your code>
```



You answer should always follow this format:
Reasoning:<Your reasoning process to solve the problem>
Action:

```python
<your code>
```


When you get the code result which fulfill the user's query. You can finish the Task, Make a formal response to user, do not use codeinterpreter.
WARNING: NO code response means the end of the task. Make sure you have fulfill user's query before you response without code
Some notice: 
1. When you want to draw a plot, use plt.save() and print the image path in markdown format instead of plt.show()
2. Your code should have proper output, responsing to user's query
3. The variable in your past code can be used directly in new code snippt.
4. End the process when you complete the task, When you do not have Action(Code), Use: Finished: <summary the analyse process and make response>
5. For summarize tasks, you can simply use your codeinterpreter to  read the content and make a summary
6.Each of your code need a output, it could be the result of calculation, the output file path and the content of file you have read. At least, you need print a "Excute Success" in the end of your code
7.Your code will be considered as a string, so use "\n" or "\\n" carefully 
8.# Use the 'collections.abc' module for a more updated approach:
    from collections.abc import Mapping
'''


if __name__ =="__main__":
    #task_list=["Cacluate 2^10000 for me!"]
    #task_list=load_data("/data/zyl7353/ReAct/TextData/a")
    chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)
    #execute_code()

    for file in os.listdir("/data/zyl7353/ReAct/TextData/arxivpapers")[20:]:
        filePath="/data/zyl7353/ReAct/TextData/arxivpapers/{}".format(file)
        task =load_data(filePath)
        print(filePath,task)
        #break
        if "pdf" not in filePath:
            if "txt" not in filePath:
                continue
        #print(filePath)
        #task="Draw a word cloud"
        #tool=PythonAstREPLTool()
        #rsp=execute_code("import PyPDF2\nprint('Success')",tool)
        #print(rsp)
        #break
        nb = nbformat.v4.new_notebook()

        messages=[{"role":"system","content":system_prompt},{"role":"user","content":"[INFO] The data is uploaded to {}".format(filePath)},{"role":"user","content":task}]
        for i in range(5):
            rsp=chat.chat_sync(system_prompt=system_prompt,messages=messages)
            print("LLM Response:\n",rsp)
            try:
                code=rsp.split("```")[-2]

                code=code.replace("python","")
                print("Code:\n",code)
                code_result=execute_code(code)
                print("codeResult:\n",code_result)
                if "error" in code_result:
                    roll_back()
                messages.append({"role":"ai","content":rsp})
                messages.append({"role":"user","content":"The code result is"+code_result})
            except:
                traceback.print_exc()
                messages.append({"role":"ai","content":rsp})
                break
        
        with open("./Text0529_pdf.jsonl","a") as f:
            json_string=json.dumps(messages,ensure_ascii=False)
            f.write(json_string+'\n')
            print("write Json!")
            
        
            






