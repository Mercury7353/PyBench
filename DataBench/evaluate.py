'''
Use gpt-4 evaluate the trajectory data of DataBench
Evaluate Pass Rate and Success rate(Compare to gpt-3.5 prompt)
Use gpt-4 to evaluate the chat history and evaluate which is better
'''


import sys
sys.path.append("/home/jeeves/zyl/zyl7353/CodeInterpreter/ReAct/ReAct")
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
#user =ChatClient(app_code='CodeAndFunction',user_token=user_token,model_id=20)
import json

def read_and_print_lines(file1_path, file2_path):
    

# Replace 'file1.jsonl' and 'file2.jsonl' with the paths to your JSONL files
read_and_print_lines('file1.jsonl', 'file2.jsonl')


if __name__ =="__main__":
    evaluate_system_prompt=''' You are a code reviewer who is responsible for select a better solution from two agent's trajectories on sloving a code problem. 
The file and user query provided for each agent is same. Just evaluate their solutions on code correctness, code result, efficiency, and final response to user
You should reasoning carefully before making decision
follow this example format:
Reason:Agent 1,.... While Agent 2,.... ,so Agent 1's solution is better
Decision:Agent 1
'''
    user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
    chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)


    input='''
    Now decide which agent's solution is better and give the reason
            Agent 1's solution:\n{line1}\n
            Agent 2's solution:\n{line2}\n
           '''
    
    with open("gpt35_codeact.jsonl", 'r', encoding='utf-8') as file1, open("gpt4_codeact.jsonl", 'r', encoding='utf-8') as file2:
        while True:
            line1 = file1.readline()
            line2 = file2.readline()
            
            # Check if both files have reached EOF
            if not line1 and not line2:
                break
            
            # Print line from first file if not EOF
            
            
            # Print a blank line to separate the sets
            print()
            rsp=chat.chat_sync(system_prompt=evaluate_system_prompt, messages=[{"role":"user","content":input.format(line1=line1,line2=line2)}])
            print(rsp)
            break