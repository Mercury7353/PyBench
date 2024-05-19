"""
This file aims to generate strong stf data, to help llama3-8b learn the ability to debug. (Learn from gpt-3.5-turbo)
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


"""

import sys

sys.path.append("..")
# sys.path.append("/home/jeeves/zyl/zyl7353/CodeInterpreter/ReAct/ReAct/redebug")
import json

# from DataGen import system_prompt_template
# from GPT import GPT
# from llmcenter import ChatClient
import re
import traceback
from os import system

from langchain_experimental.tools.python.tool import PythonAstREPLTool

# from exact_query import generate_exact_query
from llama3 import LlaMa3


def execute_code(code_str: str, tool: PythonAstREPLTool):
    try:
        result = tool.invoke(code_str)
        result = str(result)
        return result
    except:
        return traceback.format_exc()


def _execute_code(code_str: str):
    import nbformat
    from nbclient import NotebookClient

    # print("codeSTr",code_str)
    # 创建一个新的notebook对象
    code_str = code_str.replace("\\n", "\n")

    # 添加一个包含代码的cell
    nb.cells.append(nbformat.v4.new_code_cell(code_str))

    total_cells = len(nb.cells)

    # 执行notebook
    client = NotebookClient(nb)
    try:
        client.execute()
    except Exception as e:
        # print("Code error")

        # error_message=traceback.format_exc()
        error_message = str(e)
        # split('Traceback')[-2]
        # print(error_message)
        # ()
        return error_message

    # 提取执行结果
    # outputs = nb.cells[-1].outputs
    # print("CheckOutput",nb_c.cells[-1]['outputs'][0])
    outputs = nb.cells[-1]["outputs"]  # [0]['data']['text/plain']
    # print("Output",outputs)

    result = ""
    for output in outputs:
        # print("check point:",output.output_type)
        if output.output_type == "stream":  # 如果输出是标准输出或标准错误
            result += output.text
        elif output.output_type == "execute_result":  # 如果输出是执行结果
            result += str(output["data"]["text/plain"])
        elif output.output_type == "error":  # 如果输出是错误
            result += "Error: " + str(output.ename) + "\n"
            result += str(output.evalue) + "\n"
            result += "".join(output.traceback) + "\n"
    # print(result)
    return result


def roll_back():
    nb.cells.pop()
    return nb


def startVLLM():
    system("bash /data/zyl7353/CodeInterpreter/ObjLLaMa/vllm/examples/initialChat.sh")
    return


def extract_code(rsp):
    # extract code to excute from rsp
    rsp = str(rsp)

    # 正则表达式
    # print("CheckRSP",rsp)
    # 正则表达式
    pattern = r'excute_python\(code=(["\'])(.*?)\1\)'
    # 定义正则表达式
    pattern = r'excute_python\(code=(["\'])([\s\S]*?)\1\)'
    # 使用re.findall查找所有匹配项
    match = re.search(pattern, rsp)
    # 打印匹配到的内容
    if match:
        # print("MATCH Check",match)
        code = match.group(2)
        if "\\n" in code:
            code = code.replace("\\n", "\n")
            print("Format Error Fixed")
        if "```" in code:
            code = code.replace("```", "")
        if "python" in code:
            code = code.replace("python", "")
        if '''\\"''' in code:
            code = code.replace('"', '"')
        if "\\'" in code:
            code = code.replace("'", "'")

        return code

    code = parse_code_argument(rsp)
    if "\\n" in code:
        code = code.replace("\\n", "\n")
        print("Format Error Fixed")
    if "```" in code:
        code = code.replace("```", "")
    if "python" in code:
        code = code.replace("python", "")
    if '"' in code:
        code = code.replace('"', '"')
    if "'" in code:
        code = code.replace("'", "'")
    return code


def _extract_code(rsp):
    # if "<|tool_call|>" in rsp:
    #    rsp=rsp.replace("<|tool_call|>","```")
    try:
        code = rsp.split("```")[-2]
        code = code.replace("python", "")
    except:
        code = ""
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
    system_prompt_template = """ You are an AI Agent who is proficient in writing image processing code through opencv or another packages.
Each round, you are going to get a user query.
The user is a newbie in writing opencv code.  To enhance your code quality, you need to wirte comment BEFORE each line of code who has multi pairs of '()' or '[]' and clarify exactly how many pairs are needed.
So you must tell the user the reasoning process when you write your code and how the code work when it is excuted in detail and then You should return your code in the following format:

```python
<Your python code with comment before each line>
```

Your answer should ALWAYS use the following format:

Reasoning: Detailed explaination of the code
Action:(The action to complete Todo)
```python
<Your python code with comment before each line>
```

example:
Reasoning: I need to calculate 1+1+1
Action:
```python
# Need 1 pair of '()'
print(1+1)
```

When you received a message telling you there is a bug in your code, you should think step by step why the bug occurs and write the fixed full snippet of the code.
You must write a comment for the line with the bug!!!! Or you will be punished!!

You must follow this format strictly!!!!
example:
error message: ...[line15] plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)))...
 SyntaxError: unmatched ')' in line 15
Reasoning: Here is an extra ')' in the end of code, I am going to remove it.
Action:
```python
...
# Need 2 pair of '()'
plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
...
```


Notice:
1. You should always output a image through plt.savefig or cv2.imwrite. There is no need to use plt.show or cv2.imshow, You should save the processed image at :./output/{index}.png , for multi output files you can use {index}_0,{index}_1,... as file name
2. You must write comment for each line of your code, the comment should not only explain the code's function, but also show the running process of the code
3. Only one snippet of code for each response
4. Any line in your code with multi pair of '()','[]' need a commend before wirting the line
example:
```python
# Need 2 pair of '()' in this line:
plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
```

"""

    # system_prompt_template
    # startVLLM() # 会占用当前bash，需要另外单独启动

    tools = [
        {
            "name": "excute_python",
            "description": "excute the python code and get result, in the beginning of your code, you must write few lines of comment telling why you write this code",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code is going to be excuted",
                    },
                },
                "required": ["code"],
            },
        }
    ]
    # print("in")

    LLM = LlaMa3(tools=None)
    with open("task.json") as f:
        json_str = f.read()
        test_data = json.loads(json_str)
    # print(test_data)
    pass_count = 0.0
    for task in test_data:
        tool = PythonAstREPLTool()
        print("Task:\n", task["user"])
        flag = 0
        turns = []
        # print(task.keys())
        file_path = task["file_path"]
        user_query = task["user"]
        index = task["index"]
        # 清空所有单元
        # nb.cells = []

        code_result = execute_code(
            """import os
current_path = os.getcwd()
print("当前执行路径是:", current_path)""",
            tool,
        )
        print("Code Result:", code_result)
        messages = [
            {"role": "system", "content": system_prompt_template.format(index=index)},
            {
                "role": "user",
                "content": "[INFO]The image is uploaded to {file_path}".format(
                    file_path=file_path
                ),
            },
            {"role": "user", "content": user_query},
        ]
        for _ in range(3):
            rsp = LLM.chat(messages=messages)
            code = _extract_code(rsp)
            # print(len(code))
            if len(code) == 0:
                code = extract_code(rsp)
            print("Response:\n", rsp)
            print("Code:\n", code)
            code_result = execute_code(code, tool)
            if "Error" not in code_result:
                # print("CodeResult:\n",code_result)
                print("CodeResult:\n", code_result)
                messages.append({"role": "assistant", "content": rsp})
                pass_count += 1
                flag = 1
                turns.append(_ + 1)
                break
            elif (
                "If you are on Ubuntu or Debian, install libgtk2.0-dev and pkg-config, then re-run cmake or configure script in function 'cvShowImage'"
                in code_result
            ):
                print("Just Warning")
                # roll_back()
                break
            else:
                # code_result=code_result.split("\n")[-2]
                print("ErrorMessage\n", code_result)
                # roll_back()
                messages.append({"role": "assistant", "content": rsp})
                messages.append(
                    {
                        "role": "user",
                        "content": "Please Debug:{error}".format(error=code_result),
                    }
                )

        if flag == 0:
            turns.append(3)
        with open("qwen_ours_0518.jsonl", "a") as f:
            json_string = json.dumps(messages, ensure_ascii=False)
            f.write(json_string + "\n")
            print("write jsonl")
    print(turns)
    print("Average Truns: ", sum(turns) / len(turns))
    print("Pass count", pass_count)
    print("Pass rate", pass_count / len(test_data))


if __name__ == "__main__":
    # nb = nbformat.v4.new_notebook()# A Global notebook
    print("Start")
    main()

# 解析：
# excute_python(code="\\nimport pandas as pd\\nimport matplotlib.pyplot as plt\\nfrom textblob import TextBlob\\n\\n# Read in the data\\nmovies = pd.read_csv(\'100 Best Movies on Netflix_shuffled.csv\')\\n\\n# Extract the critics\' consensus for each movie\\nconsensus = movies[\'Critics Consensus\']\\n\\n# Analyze the sentiment of the critics\' consensus\\nsentiment = [TextBlob(text).sentiment.polarity for text in consensus]\\n\\n# Generate a bar plot of the movie ratings\\nratings = movies[\'Rating\']\\nplt.bar(movies[\'Title\'], ratings)\\nplt.title(\'Movie Ratings\')\\nplt.xlabel(\'Title\')\\nplt.ylabel(\'Rating\')\\nplt.show()\\n\\n# Print the sentiment scores\\nprint(sentiment)\\n")
