'''
#Generate Audio Process Data
'''
# CodeAct...
from llmcenter import ChatClient
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import traceback
import json
import nbformat
from nbclient import NotebookClient

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
You are are helpful assistant who is familiar with process audio file(mp3,wav...). The user will upload a audio file to certain file_path. 
You should write python code to fulfill the user requirement. Please only use python packages,do not use ffmpeg,ffprobe or something like that! Or you will be punished severely
You are equipped with a python codeinterpreter, which receive your code and give your the execution result of the code. You should use packages like audioread,librosa,PyAudio,pydub and write python code
You can call the codeinterpreter in the following format:
<|execute_start|>
```python
<your code>
```
<|execute_end|>


You answer should always follow this format:
Reasoning:<Your reasoning process to solve the problem>
Action:
<|execute_start|>
```python
<your code>
```
<|execute_end|>


When you finished the Task, Make a formal response to user(markdown format), do not use codeinterpreter.
Notice:
Use plt.savefig() instead of plt.show()
Save the image or anything you generate and show it via markdown format
'''


if __name__ =="__main__":
    audio_task_list= [
    # Draw the Mayer spectrum of this audio
    "Generate the Mayer spectrum for this sound file",
    "Create a Mayer spectrum visualization for this audio",
    "Plot the Mayer spectrum of this audio track",
    "Display the Mayer spectrum for this audio file",
    "Show the Mayer spectrum of this sound",
    "Render the Mayer spectrum for this audio clip",
    "Illustrate the Mayer spectrum of this audio",
    "Produce the Mayer spectrum for this audio recording",
    "Draw a Mayer spectrum for this sound clip",
    "Construct the Mayer spectrum for this audio file",

    # Increase the volume in this audio by 10%
    "Boost the volume of this audio by 10%",
    "Raise the volume of this sound by 10%",
    "Amplify the volume of this audio by 10%",
    "Increase the loudness of this audio by 10%",
    "Turn up the volume of this audio by 10%",
    "Enhance the volume of this audio by 10%",
    "Make this audio 10% louder",
    "Add 10% to the volume of this audio",
    "Elevate the volume of this sound by 10%",
    "Augment the volume of this audio by 10%",

    # 把这个两个音频拼接起来，中间用淡出处理
    "Merge these two audio files with a fade-out effect in between",
    "Combine these two audio clips with a fade-out transition",
    "Join these two audio tracks with a fade-out in the middle",
    "Stitch these two audio files together using a fade-out effect",
    "Blend these two audio recordings with a fade-out transition",
    "Fuse these two audio clips with a fade-out effect in between",
    "Integrate these two audio files with a fade-out in the middle",
    "Link these two audio tracks with a fade-out transition",
    "Connect these two audio files using a fade-out effect",
    "Attach these two audio clips with a fade-out in the middle",

    # Decrease the volume by 100%
    "Reduce the volume of this audio to zero",
    "Mute this audio file",
    "Lower the volume of this audio by 100%",
    "Turn off the sound of this audio",
    "Silence this audio track",
    "Cut the volume of this audio completely",
    "Drop the volume of this audio to zero",
    "Remove all sound from this audio",
    "Set the volume of this audio to zero",
    "Make this audio completely silent",

    # cut the first 30 seconds of the audio file and save it to a new file
    "Extract the first 30 seconds of this audio and save it as a new file",
    "Clip the initial 30 seconds of this audio and save it separately",
    "Cut the first 30 seconds from this audio and create a new file",
    "Save the first 30 seconds of this audio to a new file",
    "Trim the first 30 seconds of this audio and save it as a new file",
    "Take the first 30 seconds of this audio and save it to a new file",
    "Isolate the first 30 seconds of this audio and save it separately",
    "Save a new file with the first 30 seconds of this audio",
    "Extract and save the first 30 seconds of this audio to a new file",
    "Create a new file with the first 30 seconds of this audio",

    # 检测音频中的静音部分，自动将音频文件分割成多个片段
    "Detect silent parts in the audio and automatically split it into segments",
    "Identify silence in the audio and divide it into multiple parts",
    "Find silent sections in the audio and split the file into segments",
    "Locate silence in the audio and automatically segment it",
    
    # Put these two audio clips on top of each other
    "Overlay these two audio clips",
    "Layer these two audio files on top of each other",
    "Superimpose these two audio tracks",
    "Put one audio clip on top of the other",
    "Overlay these two audio files together"
]

    chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)

    for task in audio_task_list[56:]:
        print("Task:   ",task)
        nb = nbformat.v4.new_notebook()
        messages=[{"role":"system","content":system_prompt},{"role":"user","content":"[INFO]The file is uploaded to {}".format("/data/zyl7353/ReAct/data/Ghostrifter Official - Serenity.mp3")},{"role":"user","content":task}]
        for i in range(5):
            rsp=chat.chat_sync(system_prompt=system_prompt,messages=messages)
            print("LLM Response:\n",rsp)
            try:
                code=rsp.split("```")[-2]

                code=code.replace("python","")
                print("Code:\n",code)
                print("Code:\n",code)
                code_result=execute_code(code)
                print("codeResult:\n",code_result)
                if "error" in code_result:
                    roll_back()
                #print("codeResult:\n",code_result)
                messages.append({"role":"ai","content":rsp})
                messages.append({"role":"user","content":"The code result is"+code_result})
            except:
                traceback.print_exc()
                messages.append({"role":"ai","content":rsp})
                break
        
        with open("./Audio_codeact_0529.jsonl","a") as f:
            json_string=json.dumps(messages,ensure_ascii=False)
            f.write(json_string+'\n')
            print("write Json!")
            
        
            






