import gradio as gr
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

    <TEXT>
    Args:
        response (str): The chatbot response.

    Returns:
        str: Extracted code.
    """
    try:
        code=response.split("```")[-2]
        code=code.replace("python","")
    except:
        code=None
    return code
LLM = LlaMa3(tools=None)

def chat(message, chat_history, tool):
    chat_history.append({"role": "user", "content": message})
    print("Chat History\n",chat_history)
    response_total=""
    round=0
    while True:
        round+=1
        if round>5:
            break
        response = LLM.chat(messages=chat_history)
        response_total+=response
        print("Response\n",response)
        chat_history.append({"role": "assistant", "content": response})

        code = extract_code(response)
        print("Code\n",code)
        if code:
            result = execute_code(code, tool)
            print("CodeResult\n", result)
            response_total+="\n\n\n Code Result:\n```markdown\n"+result+"\n```\n\n\n"
            chat_history.append({"role": "system", "content": result})
        else:
            break

    return response_total

def init(message,history):
    print("Message\n",message)
    print("History\n",history)
    #history.append((None,message))
    #history=history[:-1]

    tool = PythonAstREPLTool()
    chat_history = [{"role":"system","content":system_prompt}]
    full_message = chat(message, chat_history, tool)
    message=None
    return full_message

gr.ChatInterface(
    init,
    chatbot=gr.Chatbot(height=500),
    textbox=gr.Textbox(placeholder="Input your query and file path", container=False, scale=7),
    title="CodeInterpreter",
    description="Ask CodeInterpreter any question",
    theme="soft",
    examples=["Analyse the csv file for me and select proper images to visualize the data", "Merge these two images vertically", "Summarize the novel and draw a word cloud on the previous 1000 words"],
    cache_examples=True,
    retry_btn=None,
    undo_btn="Withdraw",
    clear_btn="Clear",
).launch(share=True)

# [INFO] The file is uploaded to .IRIS.csv Please draw a bar plot to visualize the feature distibution of different kinds of iris. Use markdown to show you image_result!
# [INFO] The file is uploaded to ./IRIS.csv.             Explore the data and draw a bar plot to visualize the data. Use markdown to show you image_result!
'''
import gradio as gr

with gr.Blocks() as demo:
    gr.Chatbot([
        ("Show me an image and an audio file", "Here is an image"), 
        (None, ("lion.jpg",)), 
        (None, "And here is an audio file:"), 
        (None, ("cantina.wav",))
    ]).style(height=1000)

demo.launch()
'''