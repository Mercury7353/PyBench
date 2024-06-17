'''
封装一下  带有code interpreter的 assistant
'''
import os
import json
from openai import AzureOpenAI
import time
from IPython.display import clear_output
from .save_notebook import generate_notebook, save_as_ipynb

import filetype

def identify_file_type(file_bytes):
    kind = filetype.guess(file_bytes)
    if kind is None:
        return 'Unknown file type'
    return kind.mime

import ast
import re

def extract_inputs_from_runsteps(data):
    # 定义正则表达式来匹配 input 和 logs 字段，确保引号类型一致
    input_pattern = re.compile(r'input=(["\'])(.*?)\1', re.DOTALL)
    output_pattern = re.compile(r'logs=(["\'])(.*?)\1', re.DOTALL)

    # 使用 findall 方法找到所有匹配项
    input_matches = [match[1] for match in input_pattern.findall(data)]
    output_matches = [match[1] for match in output_pattern.findall(data)]

    # 返回两个列表
    return input_matches, output_matches

class GPT():
    def __init__(self,output_path) -> None:
        self.name="test-code-interpreter"# deployment name
        
        self.client,self.assistant,self.thread=self._init_assistant()
        self.output_path=output_path
        
        
        
    def _init_assistant(self):
        print("Start init assistant......")
        client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        # "76e7f58cac704a93bfffa2e34164cd85"
        api_version="2024-02-15-preview",
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        # "https://code-interpreter.openai.azure.com/"
        )
        assistant = client.beta.assistants.create(
            name="Data Analyst",
            instructions=f"You are a helpful AI assistant who is good at write python code to slove user's problem"
            f"You have access to a sandboxed environment for writing and testing code."
            f"When you are asked to solve a problem you should follow these steps:"
            f"1. Think about the plan to solve the problem before your code"
            f"2. Write the code. Any code you write should return to user after the code is executed successfully the reasoning process and use ```<code>``` format"
            f"3. Anytime you write new code display a preview of the code to show your work."
            f"4. Run the code to confirm that it runs."
            f"5. If the code is executed successfully. Analyse the code result and think about next step to do"
            f"6. Return anything the code generated,not only the image, but also the chart, head of data or modified file."
            f"7. If the code is unsuccessful display the error message and try to revise the code and rerun going through the steps from above again."
            f"8. Do not ask the user before you complete all the requirements. Make decision by yourself!",
            tools=[{"type": "code_interpreter"}],
            model=self.name #You must replace this value with the deployment name for your model.
        )
        print("Assistant Created")
        thread=client.beta.threads.create()
        

        return client,assistant,thread

    def _add_message(self,message,file_path):
        try:
            file_list=self._upload_file(path_list=file_path)

        except:
            file_list=[]

        self.client.beta.threads.messages.create(
        thread_id=self.thread.id,
        role="user",
        content=message,
        
        file_ids=file_list
    )
        
    def _upload_file(self,path_list):
        file_list=[]
        for path in path_list:
            file = self.client.files.create(
            file=open(path, "rb"),
            purpose='assistants'
            )
            print("File Uploaded: ",file.id)
            file_list.append(file.id)
        return file_list
        
    def chat(self,message,path,index):
        start_time = time.time()
        self._add_message(message,path)
        run=self.client.beta.threads.runs.create(
        thread_id=self.thread.id,
        assistant_id=self.assistant.id,
        #instructions="New instructions" #You can optionally provide new instructions but these will override the default instructions
        )

        status = "queued"
        
        while status not in ["completed", "cancelled", "expired", "failed"]:
            time.sleep(5)
            run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id,run_id=run.id)
            print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
            status = run.status
            print(f'Status: {status}')
            clear_output(wait=True)

        print(f'Status: {status}')
        print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
        messages = self.client.beta.threads.messages.list(
        thread_id=self.thread.id
        )
        data = json.loads(messages.model_dump_json(indent=2))  # Load JSON data into a Python object
        response= self.format_message(data)
        #print(data)
        #print(response)
        run_steps = self.client.beta.threads.runs.steps.list(
        thread_id=self.thread.id,
        run_id=run.id
        )
        #print(run_steps)
        run_info_str=str(run_steps)
        print("Start CheckPoint\n\n\n",run_info_str,"\n\n\nEnd Check Point")
        code,result=extract_inputs_from_runsteps(run_info_str)
        #print(code,result)
        print("Code:\n",code)
        print("CodeResult:\n",result)
        print(response)
        self.save_file(response,index,code,result)


    def format_message(self,data):
        
        #输入一个json（dict），解析出value键的值，annotations的值
        results = []
        # Iterate through each message in the 'data' list
        for message in data.get('data', []):
            # Initialize a dictionary to store the parsed data 
            parsed_data = {
                'value': '',
                'annotations': [],
                'file_ids': []
            }
            
            # Iterate through each content item in the 'content' list
            for content_item in message.get('content', []):
                # Check if the content item has a 'text' key
                if 'text' in content_item:
                    text_content = content_item['text']
                    parsed_data['value'] = text_content.get('value', '')
                    parsed_data['annotations'] = text_content.get('annotations', [])
                # Check if the content item has an 'image_file' key
                elif 'image_file' in content_item:
                    image_file_content = content_item['image_file']
                    parsed_data['file_ids'].append(image_file_content.get('file_id', ''))
            
            # Get the 'file_ids' from the message
            parsed_data['file_ids'].extend(message.get('file_ids', []))
            
            # Append the parsed data to the results list
            results.append(parsed_data)

        return results

        


    def save_file(self,data,index,code,result):
        file_list=[]
        file_ids=[]
        for dic in data:
            file_list.extend(dic["annotations"])
            file_ids.extend(dic["file_ids"])
        
        file_name_list=[]
        for file_id in file_ids[:-1]:
            try:
                content = self.client.files.content(file_id)
            except:
                continue
            #file= content.write_to_file("sinewave.png")
            #print(content)
            file_bytes=content.read()
            file_type=identify_file_type(file_bytes)
            print(file_type)
            file_suffix=str(file_type).split("/")[-1]
            with open("/data/zyl7353/codeinterpreterbenchmark/output/{}.{}".format(index,file_suffix), "wb") as download_file:
                download_file.write(file_bytes)
                print("File Saved")


        messages=[{"role":"system","content":"you are a helpful assistant"}]
        round=0
        user_flag=0
        cells=[]
        for msg in data[::-1]:
            if user_flag==0:
                user_query=msg['value']#.decode('utf-8')
                messages.append({"role":"user","content":user_query})
                cells.append({"role": "user", "text": user_query})
                user_flag=1

            else:
                content=msg['value']#.decode('utf-8')
                messages.append({"role":"assistant","content":content})
                cells.append({"role": "assistant", "text": content})

                round=round-1
                try:
                    current_code=code[round].replace("\\n","\n").replace("\\r","\r")
                    current_code_result=result[round].replace("\\n","\n").replace("\\r","\r")
                    messages.append({"role":"assistant","content":current_code})
                    cells.append({"role": "assistant", "code": current_code,"result":current_code_result})

                    messages.append({"role":"tool","content":current_code_result})
                except:
                    continue

        full_message={"messages":messages,"index":index}




        with open(self.output_path,"a") as json_file:
            json_string=json.dumps(full_message)
            json_file.write(json_string+"\n")
            print("Json writed")
            #从-1开始向前遍历，每隔一个加上两条message : 首先加 assistant : 代码，然后加 tool:output，作为code result
            #这个也是栈
        save_as_ipynb(generate_notebook(cells), f"cells/{index}.ipynb")
    

    