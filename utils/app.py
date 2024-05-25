import gradio as gr
import random
import time
from llama3 import LlaMa3
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import traceback
import json
import re

system_prompt = '''
You are an AI Agent who is proficient in solving complicated tasks. Each step, you should first think step by step according to user query and previous messages. The code you write will be appended to a notebook as a new cell. You will get the execution result of the cell.
When you find your code is error, your last code is removed from the notebook, which means you should rewrite the whole cell (redefine all variables).
You should return in markdown format
You are equipped with a code interpreter, which will execute your code and return the code result. You must read and process the uploaded file to fulfill user's requirements.
You could use the code interpreter in this format:
<|execute_start|>
```python
<your code>
<|execute_end|>
Constraints:
1. You cannot ask the user, clarify the question by yourself.
2. Each of your responses must contain code, unless the task is completed or the code is unnecessary.
3. You should write your reasoning process before your code.
4. When you finish the task. You should make a formal response. Please Use markdown format to show the image 
5. Save anything to current folder. Return in markdown 

Example:
Finished:
![Processed Image](./train_val_accuracy.jpeg)

'''

def execute_code(code_str: str, tool: PythonAstREPLTool):
    """Execute python code and return the execution result.

    Args:
        code_str (str): The code to be executed.
        tool (PythonAstREPLTool): Python AST REPL tool.

    Returns:
        str: Code execution result.
    """
    try:
        result = tool.invoke(code_str)
        result = str(result)
        return result
    except:
        return traceback.format_exc()

def extract_code(response):
    """Extract code from the chatbot response.

    Args:
        response (str): The chatbot response.

    Returns:
        str: Extracted code.
    """
    try:
        code = response.split("```")[-2]
        code = code.replace("python", "")
    except:
        code = None
    return code

def extract_image_filename(input_string):
    # 匹配类似 /private/var/folders/... 的路径
    pattern = r'/private/var/folders/[^\s]+'
    match = re.search(pattern, input_string)
    if match:
        # 去掉路径末尾的多余字符
        path = match.group(0)
        # 去掉末尾的反引号和句号
        path = re.sub(r'[`\.]+$', '', path)
        return path
    else:
        return False

def remove_duplicates_preserve_order(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

LLM = LlaMa3(tools=None)

def chat(message, chat_history, tool):
    chat_history.append({"role": "user", "content": message})
    print("Chat History\n", chat_history)
    assistant_history = []
    response_total = ""
    round = 0
    while True:
        round += 1
        has_image = 0
        if round > 5:
            break
        response = LLM.chat(messages=chat_history)
        response_total += response

        print("Response\n", response)
        image_path = extract_image_filename(response)
        if image_path == False:
            assistant_history.append((None, response))
        else:
            assistant_history.append((None, response))
            assistant_history.append((None, (image_path,)))
            has_image = 1
        chat_history.append({"role": "assistant", "content": response})

        code = extract_code(response)
        print("Code\n", code)
        if code:
            result = execute_code(code, tool)
            print("CodeResult\n", result)
            result = result.replace("sandbox:", ".")
            image_path = extract_image_filename(result)
            if image_path == False:
                assistant_history.append((None, "\n\n\n Code Result:\n```markdown\n" + result + "\n```\n\n\n"))
            else:
                if has_image == 0:
                    assistant_history.append((None, "\n\n\n Code Result:\n```markdown\n" + result + "\n```\n\n\n"))
                    assistant_history.append((None, (image_path,)))
            response_total += "\n\n\n Code Result:\n```markdown\n" + result + "\n```\n\n\n"
            chat_history.append({"role": "system", "content": result})
        else:
            break
    return assistant_history

def init(message, files, history):
    print("Message\n", message)
    print("Files\n", files)
    print("History\n", history)
    tool = PythonAstREPLTool()
    chat_history = [{"role": "system", "content": system_prompt}]

    if files:
        file_info = "\r".join([f"[INFO] The file is uploaded to {file.name}." for file in files])
        message = f"{file_info}  \r {message}"
        print("Check", message)
    assistant_history_full = chat(message, chat_history, tool)
    message = None
    return "", assistant_history_full

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(height=800)
    msg = gr.Textbox(placeholder="Input your query and file path", container=False, scale=7)
    file_upload = gr.Files(label="Upload files")
    submit_btn = gr.Button("Submit")
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history, files):
        _, assistant_history_final = init(message, files, chat_history)
        chat_history.append((message, None))
        chat_history.extend(assistant_history_final)
        
        print("CheckPoint\n", chat_history)
        return "", chat_history

    submit_btn.click(respond, [msg, chatbot, file_upload], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(share=True)
