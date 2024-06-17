# generate codeinterpreter data
'''
log 20240411:
Generate Data in this pipeline:
User Instruction（已经用tiny- story的method造好了） 
——>  Plan(DAG)直接复用(结构化，多样化)  
——> 还是生成一个串行的路径 
——> 作为Initial Plan 
—> 每个step让gpt3.5 生成 Plan , Current Step todo , Code 的片段 
——> 然后不用user feedback了
——> 直接是assistant - tool 这样的对话pair

用户只上传数据集，不上传query呢？  直接reject!
'''
'''
This version is tailored for generate trajectory for DataScience Tasks. 
Normally, the user first upload a file to a given file_path
The assistant should first load the file and answer questions
In this version, I will add GPT-4-1106-preview / gpt-3.5-turbo. Or a fixed agents who select random datascience tasks
!!!In this part, we can use the method of DataInterpreter, 
which means we decompose the general area "DataScience" to several small and specific tasks(following a DAG structure)
After that, user agent should adjust the task from the return of the assistant agent. 
eg. Generate query suitable for the current dataset in the give DAG task area. 
"Draw a line chart" --- generate from "DataVisualization" Node in DAG. 
'''

'''
Log 20240314:
Update Plan:
Add code review phrase: Use Reflexion to refine the code:
Some reflexion triggers: 
1. plt.show() must change to plt.save() and print the path
2. Observation is None ---> let's print the result
3. Error: review the code 

If the code pass the code review phase:
Summary of the code : return to AI user.
'''

'''
log 20240415:
画图的结果很抽象，估计是dataset和query不匹配的结果
这样修改一下：首先define一个提问者
head data的前几行，再根据数据集具体情况生成query
'''
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
from exact_query import generate_exact_query
# multi-turn conversation
user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)
user =ChatClient(app_code='CodeAndFunction',user_token=user_token,model_id=20)


tools = [
            {"name": "excute_python", "description": "Excute python code and get result",
            "parameters": {"type": "object", 
            "properties":
            {"code": 
            {"type": "string", "description": "The code need to be excuted"}}, 
            "required": ["code"]}}
]

tool_names = ["excute_python"]

system_prompt_template = """You are an AI Agent who is proficient in solve complicated task. Each step, you could reconsider the Plan(which should no more than 5 steps), generate specific Todo for current step and write code.
Each subtask in the plan should be a task need to be complete by code. You are equipped with a codeinterpreter. You can call it in the following format, then you will get the result of your code.
```python
<Your python code>
```


Each round, your answer should ALWAYS use the following format:
<|start_of_text|>
Analyse: Analyse the user input or the result of your excuted code
This Step Todo: (The subtask you need to complete at current step, it could be fix the bug or excuet the plan)
Action:(The action to complete Todo)
```python
<Your python code>
```
<|end_of_text|>

You will got the result of your code after each step. When the code of previous subtask is excuted successfully, you can write and excuet the code for next subtask
When you complete all subtasks(completely fulfill the user query), you should summarize the previous analyse process and make a formal response to user, The response should follow this format:

Finished: <Answer to user query>


Some notice: 
1. When you want to draw a plot, use plt.save() and print the image path in markdown format instead of plt.show()
2. Your code should have proper output, responsing to user's query
3. The variable in your past code can be used directly in new code snippt.
4. End the process when you complete the task, When you do not have Action(Code), Use: Finished: <summary the analyse process and make response>


"""
# Begin! Remind to always use the exact characters `Final Answer` when responding.
system_prompt_template_review="""Following the code instruction strictly. You have to write python code to solve the problem

Here is an example
```python

print("hello world")


```

ALWAYS use the following format:

Question: the input question you must answer

Thought: you should always think about what to do

Action:

```python
code

```


... (this Thought/Action/Observation can repeat N times)

Thought: I now know the final answer

Final Answer: the final answer to the original input question
Some notice: 
1. When you want to draw a plot, use plt.save() and print the image name and its path in markdown format instead of plt.show()
2. Your code should have proper output, responsing to user's query
3. The variable in your past code can be used directly in new code snippt.

"""
messages_template = [
    {"role": "user", "content": "Question: What is the result of 3 times 5?"},
    {
        "role": "ai",
        "content": """Thought: I need to call the multiply tool to calculate 3 times 5.
Action:
```python
print(3*5)
```
""",
    },
    {"role": "ai", "content": "Observation: 15"},
    {"role": "ai", "content": "Final Answer: The result of 3 times 5 is 15."},
]

def generate_task_seq(DAG):
    '''
    generate task seq base on dataset description
    '''
    task_des_list=Generate_task_sequence(DAG)
    system_prompt={"role":"system","content":"You are ChatBot User who is willing to cooperate with an Data Scientist AI assistant to analyse a dataset\n you have a task sequence:{}, every step, you should follow its guide and generate a specific question base on history messages".format(task_des_list)}
    system_prompt=system_prompt['content']
    #print(task_des_list)
    while len(task_des_list)<1:
        task_des_list=Generate_task_sequence(DAG)
        system_prompt={"role":"system","content":"You are ChatBot User who is willing to cooperate with an Data Scientist AI assistant to analyse a dataset\n you have a task sequence:{}, every step, you should follow its guide and generate a specific question base on history messages".format(task_des_list)}
        system_prompt=system_prompt['content']
        print(task_des_list)
    

    return system_prompt,task_des_list
def generate_steptodo(system_prompt,task_des_list,step):
    '''
    Generate query from task sequences and last step response and dataset descirption
    '''
    this_step_task=task_des_list[step]
    tmp_messages=copy.deepcopy(full_messages)
    tmp_messages.append({"role":"user","content":"You should act as a chatbot user. Generate a task for this step according to the code observation and current step topic. You must take the previous code and obversation into consideration and generate a specific question! You task should be the related to {},but needs to be expressed differently and specificly. ONLY return the generated task".format(this_step_task)})
    query = user.chat_sync(system_prompt=system_prompt, messages=tmp_messages,temperature=0.9)
    print("Query:",query)
    return query
# The function seems useless....            




def Plan_Act(question,chat_history):
    codereviewer=Codereviewer()
    #print(question)
    final_act=''
    final_Obs=''
    CodePassport=False
    #messages.append({"role"})
    round_messages=[]# only store this round message: including user query, ReAct response and Code review message

    #chat_history.append({"role": "user", "content": question})
    round_messages.append({"role":"user","content":question})
    # The ReAct Process, return to user only meet final answer
    # No much reasoning / so delete "final Answer part"
    for i in range(3):
        try:
            #print(chat_history)
            #print("chat",chat_history)
            msg = chat.chat_sync(system_prompt=system_prompt_template, messages=chat_history)
            print(msg)
            # system_prompt=system_prompt_template, 
            
            #if "Final Answer" in msg:
            #    messages.append({"role": "ai", "content": msg})
            #    print("Get final Answer")
            #    print(messages)
            #    break
            
            
            #应该拆解成不同的松耦合函数的.... 
            try:
                # sometimes : There is a query do not need code
                action = msg.split('```')[-2]
                chat_history.append({'role':"ai","content":msg})
            except:
                print("No code response")
                #print("Check Point",msg)
                #if "Finished" in msg:
                chat_history.append({'role':"ai","content":msg})
                return chat_history
                break


                
                
            
        

            #print("action checkpoint",action)
            # This is a try, except pair for robust --- The LLM may response json format or Just Code
            try:
                action = json.loads(action)
                tool_name = list(action.keys())[0]
                tool_param = action[tool_name]# Just the Code!
                #CodeResult=tool_call(tool_name, tool_param)
            except:
                #print("Model 2")
                action=action.replace("python",'')
                #print("Action",action)
            CodeResult=execute_code(action)
            print("CodeResult",CodeResult)
            #print(full_messages)
            CodePassport,CodeSuggestion=codereviewer.check(question=question,code=action,CodeResult=CodeResult)
            if CodePassport==True:
                try:
                    obs = "Observation: " + CodeResult
                except:
                    obs=''
                #messages.append({"role": "ai", "content": msg})
                #messages.append({"role": "ai", "content": obs})
                # 不对！ 如果有了code passport 应该做一步obs ,code ,  和query的summary，最后的message应该是code+Observation+Summary
                final_act=action
                final_Obs=CodeResult
                #print(final_act)
                print("Over action")
                
            else:
                roll_back()
                for i in range(2):
                    print("Code Review Time:{}".format(i))
                    round_messages.append({"role":"user","content":"Modify the code. The following are instructions: \n{}\nReturn the modified code(the code should between ```<code>```)".format(CodeSuggestion)})
                    modify_msg=chat.chat_sync(system_prompt=system_prompt_template_review,messages=round_messages)
                    try:
                        action = modify_msg.split('```')[-2]
                    except:
                        #print("MSG",modify_msg)
                        raise "Format error"
                    action=action.replace("python",'')
                    #print("review action: ",action)
                    CodeResult=execute_code(action)
                    #print("Review Code Result",CodeResult)
                    if len(CodeResult)==0:
                        print(action)
                    CodePassport,CodeSuggestion=codereviewer.check(question=question,code=action,CodeResult=CodeResult)
                    #print("Code Suggestion",CodeSuggestion)
                    if CodePassport==True:
                        #Update Code and Obs
                        final_act=action
                        final_Obs=CodeResult
                        print("OverAction")
                        
                    else:
                        roll_back()
                        round_messages.append({"role":"ai","content":modify_msg})
            if final_act=='':
                # Fail to write the correct code in 5 rounds
                print("Fail code")
                chat_history.append({'role':"ai","content":"Observation:Sorry, There are some error when excuting the code,Let's skip this subtask\n" +"Code:\n```python"+str(action)+"\n```"}) 
                return chat_history
                

            else:
                chat_history.append({"role":"ai","content":"Observation:You have complete a subtask, the code result is:{code_result}".format(code_result=final_Obs)})
                return chat_history



            
            

        except Exception as e:
            #messages=messages[0:-1]
            #raise e
            #print(e)
            traceback.print_exc()
            
            print("format error: Retry request")
            continue
    
    
    
#%%
# Rewirte this function: use Xagent:nbclient to run python code and get observation
def tool_call(tool_name, tool_params):
    print("tool name",tool_name)

    if tool_name in ['excute_python']:
        result=execute_code(tool_params)
        #print("Code Result",result)
        return result
        
    else:
        print("ERROR: tool " + tool_name + " not found!")
        return None

def parsing(messages):
    '''
    turn messages in the format of function call
    '''
    ans = {}
    ans['tools'] = tools
    ans['messages'] = []
    for message in messages:
        if message['role'] == "assistant":
            if "Observation" in message['content']:
                ans['messages'].append({
                    "role": "tool",
                    "content": message['content']
                })
            else:
                ans['messages'].append(message)
        elif message['role']=='ai':
            if "Thought" in message['content']:
                tmp = {}
                tmp['role'] = "ai"
                thought, action = message['content'].split("Action:\n")
                tmp['content'] = thought
                
                action = json.loads(action.split('```')[1])
                tmp['tool_calls'] = [{
                    "name": list(action.keys())[0],
                    "arguments": action[list(action.keys())[0]]
                }]
                ans['messages'].append(tmp)
            else:
                ans['messages'].append({
                    'role': "ai",
                    'content': message['content']
                })
        elif message['role']=='user':
            ans['messages'].append(message)
    return ans


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


def getUserInstruction():
    '''
    Randomly select a user instruction from /data/zyl7353/CodeInterpreter/ReAct/BlurQueryGen/query.jsonl
    Example format: {"skill": "data", "query": "\nExtract the theme from the given dataset.\n"}
    '''
    # Define the path to the file containing user instructions
    file_path = '/data/zyl7353/CodeInterpreter/ReAct/BlurQueryGen/query.jsonl'
    
    # Read the file and load the instructions into a list
    try:
        with open(file_path, 'r') as file:
            instructions = [json.loads(line) for line in file if line.strip()]
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"An error occurred while decoding JSON: {e}")
        return None

    # Randomly select one instruction from the list
    if instructions:
        selected_instruction = random.choice(instructions)
        return selected_instruction["query"]
    else:
        print("The file does not contain any instructions.")
        return None

# Example usage:
# instruction = getUserInstruction()
# print(instruction)
    
if __name__ == '__main__':
    #DAG=Generate_DAG()# Generate a DAG randomly, this time may be shorter path, or randomly select some task?  好像也random不了太多
    for file_name in os.listdir('/home/jeeves/zyl/zyl7353/CodeInterpreter/dataset')[330:]:# Select a file
        # Randomly select a user query
        #user_instruction=getUserInstruction()# randomly select a user query from the data set
        #user_instruction="Generate a simple data report from the given dataset."
        
        
        # Select the dataset
        
        file_path='/home/jeeves/zyl/zyl7353/CodeInterpreter/dataset/{}'.format(file_name)
        if ".csv" in file_path or ".xlsx" in file_path or ".xls" in file_path:
            print("Read file:{}".format(file_name))
        else:
            continue
        #user_instruction=generate_exact_query(file_path)
        user_instruction=generate_exact_query(file_path=file_path)
        print("User Instruction:", user_instruction)
        full_messages = []
        user_messages=[]
        # Start a notebook
        nb = nbformat.v4.new_notebook()# A Global notebook
        full_messages.append({"role":"user","content":"I have upload the file to this path:{}".format(file_path)})
        full_messages.append({"role":"user","content":user_instruction})
        #print(full_messages[1])
        count=0
        answer_flag=''# The answer flag ,store the answer , check if it has finished by the CodeAgent
        while "Finished" not in answer_flag  and count<=10: 
            full_messages=Plan_Act(user_instruction,full_messages)
            try:
                answer_flag=full_messages[-1]["content"]
            except:
                break
            count+=1
            print("Round {count}".format(count=count))
            if "Finished" in answer_flag:
                break
          
            
        json_file_name = '/home/jeeves/zyl/zyl7353/CodeInterpreter/ReAct/ReAct/Multi_turn_Funcall_woplan.jsonl'

        # 使用 json.dump 方法将字典列表写入 JSON 文件
        with open(json_file_name, 'a') as wr:
            json_string=json.dumps(full_messages,ensure_ascii=False)
            wr.write(json_string+'\n')
            print("write jsonl,{}".format(file_name))

'''
with open("data_gen_result.txt", "w") as f:
    pass
with open("data_gen_result.txt", "a") as f:
    question = "A bag contains red and blue balls. The number of red balls is 4 more than twice the number of blue balls. If there are 10 red balls, how many blue balls are there?"
    res = generate_result(question, tools, tool_names, messages_template)
    #print(res)
    print(res, file=f)
'''
