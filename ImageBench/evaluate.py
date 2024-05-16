'''
Use gpt-4 evaluate the trajectory data of DataBench
Evaluate Pass Rate and Success rate(Compare to gpt-3.5 prompt)
Use gpt-4 to evaluate the chat history and evaluate which is better
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
#user =ChatClient(app_code='CodeAndFunction',user_token=user_token,model_id=20)
import json


if __name__ =="__main__":
    evaluate_system_prompt=''' You are a code reviewer who is responsible for select a better solution from two agent's trajectories on sloving a code problem. 
The file and user query provided for each agent is same.
You should evaluate both solutions in the following dimensions：
Score this dimensions from 1-10, 1 means correct irrevlant code, 10 means excellent code
Reasoning Quality: Is the reasoning process correctly analyse the user input or code feedback? give a score between 1-10
Coda Quality: Evaluate The code correctness and whether it fulfill the user query? give a score between 1-10

Then you should give the total socre of each 
You should end your response with this sentence
Decision: Agent 1 <score 1>, Agent 2 <score 2>
Notice: Both cv2.imwrite and plt.savefig is okay
'''
    user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
    chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)


    
    success=[]
    with open("gpt35_codeact.jsonl", 'r', encoding='utf-8') as file1, open("llama3-8b_codeact.jsonl", 'r', encoding='utf-8') as file2:
        while True:
            input='''
    Now decide which agent's solution is better and give the reason
            Agent 1's solution:\n{line1}\n
            Agent 2's solution:\n{line2}\n
           '''
            line1 = file1.readline()
            line2 = file2.readline()
            print("Length Test")
            print(len(line1))
            print(len(line2))
            
            # Check if both files have reached EOF
            if not line1 and not line2:
                break
            
            # Print line from first file if not EOF
            
            
            # Print a blank line to separate the sets
            print()
            rsp=chat.chat_sync(system_prompt=evaluate_system_prompt, messages=[{"role":"user","content":input.format(line1=line1,line2=line2)}])
            print(rsp)
            decision=rsp.split("\n")[-1]
            print("Decision:\n",decision)
            success.append(decision)
            
    print(success)
    count=success.count("Decision: Agent 2")
    print("Count:",count)

    print("success Rate:",count/len(success))
    