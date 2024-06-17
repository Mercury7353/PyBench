'''
Generate Math Data
'''
# CodeAct...
from llmcenter import ChatClient
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import traceback
import json


def load_data(input_file):
    """Read problems from a JSON file, sort by length, and save the top N longest problems."""
    with open(input_file, 'r', encoding='utf-8') as f:
        problems = json.load(f)

    return problems

def execute_code(code_str: str, tool: PythonAstREPLTool):
    """execute python code and return the execution result

    Args:
        code_str (str): the code to be executed
        tool (PythonAstREPLTool): python ast repl tool

    Returns:
        str: code execution result
    """
    try:
        print(code_str)
        result = tool.invoke(code_str)
        result = str(result)
        return result
    except:
        return traceback.format_exc()


user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
#chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)
system_prompt='''
You are are helpful assistant who is good at write python code to slove complex math problems
You are equipped with a python codeinterpreter, which receive your code and give your the execution result of the code.
You can call the python codeinterpreter in the following format:

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
When you asked to draw something,use you codeinterpreter! use plt.savefig() instead of plt.show() to save the item you have drawn. And give the user it's output path
'''


if __name__ =="__main__":
    task_list=[
    "Draw a dog for me, sitting and wagging its tail.",
    "为我画一只坐着摇尾巴的狗。",
    "Draw a blue star for me, with five points and a smiling face in the center.",
    "为我画一颗蓝色的星星，中间有一个笑脸。",
    "Draw a tree for me, with a thick trunk and lush green leaves.",
    "为我画一棵树，有粗壮的树干和茂密的绿叶。",
    "Draw a yellow sun for me, with rays extending outward and a pair of sunglasses.",
    "为我画一个黄色的太阳，带有向外延伸的光芒和一副太阳镜。",
    "Draw a house for me, with a red roof, blue door, and two windows.",
    "为我画一座房子，有红色的屋顶、蓝色的门和两个窗户。",
    "Draw a green leaf for me, with detailed veins and a dewdrop on it.",
    "为我画一片绿色的叶子，有详细的叶脉和一滴露珠。",
    "Draw a car for me, a red sports car with sleek lines and shiny wheels.",
    "为我画一辆车，一辆红色的跑车，有流线型的车身和闪亮的轮子。",
    "Draw a purple flower for me, with five petals and a yellow center.",
    "为我画一朵紫色的花，有五片花瓣和一个黄色的花心。",
    "Draw a bird for me, a small bluebird perched on a branch.",
    "为我画一只鸟，一只停在树枝上的小蓝鸟。",
    "Draw a rainbow for me, with all seven colors arcing across a cloudy sky.",
    "为我画一道彩虹，有七种颜色横跨在多云的天空中。"
]



    #task_list=load_data("/data/zyl7353/ReAct/MATH_base_query.json")
    chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=106)

    for task in task_list:
        print("Task:   ",task)
        tool=PythonAstREPLTool()
        messages=[{"role":"system","content":system_prompt},{"role":"user","content":task}]
        for i in range(3):
            rsp=chat.chat_sync(system_prompt=system_prompt,messages=messages)
            print("LLM Response:\n",rsp)
            try:
                code=rsp.split("```")[-2]

                code=code.replace("python","")
                print("Code:\n",code)
                code_result=execute_code(code,tool)
                print("codeResult:\n",code_result)
                messages.append({"role":"ai","content":rsp})
                messages.append({"role":"user","content":"The code result is"+code_result})
            except:
                traceback.print_exc()
                messages.append({"role":"ai","content":rsp})
                break
        
        with open("./Math.jsonl","a") as f:
            json_string=json.dumps(messages,ensure_ascii=False)
            f.write(json_string+'\n')
            print("write Json!")
            
        
            






