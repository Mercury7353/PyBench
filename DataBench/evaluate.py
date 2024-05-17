'''
Use gpt-4 evaluate the trajectory data of DataBench
Evaluate Pass Rate and Success rate(Compare to gpt-3.5 prompt)
Use gpt-4 to evaluate the chat history and evaluate which is better
gpt-4评测两个点:
1. 是否pass了,(是否完成了用户的需求),写true or false
2. 质量如何,分成code和quality两个方面来评价
'''

'''
可以加个CoT,step by step推导最终得分
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
def sum_scores(score_list):
    # 初始化Agent 1和Agent 2的总分
    total_score_agent1 = 0
    total_score_agent2 = 0
    agent1_pass_list=[]
    agent2_pass_list=[]
    # 遍历列表中的每一项
    for item in score_list:
        # 分割字符串，获取Agent 1和Agent 2的分数
        score_dict=json.loads(item)
        agent1_score = score_dict["Score"]['Agent1']
        agent2_score = score_dict["Score"]['Agent2']
        agent1_pass = score_dict["Pass"]["Agent1"]
        agent2_pass = score_dict["Pass"]["Agent2"]
        agent1_pass_list.append(agent1_pass)
        agent2_pass_list.append(agent2_pass)
        # 累加到各自的总分
        total_score_agent1 += int(agent1_score)
        total_score_agent2 += int(agent2_score)

    # 返回Agent 1和Agent 2的总分之和
    agent1_pass_count=agent1_pass_list.count("Pass")
    agent2_pass_count=agent2_pass_list.count("Pass")
    total_len=len(score_list)
    agent1_pass_rate=float(agent1_pass_count)/float(total_len)
    agent2_pass_rate=float(agent2_pass_count)/float(total_len)
    return total_score_agent1 , total_score_agent2 ,agent1_pass_rate,agent2_pass_rate





if __name__ =="__main__":
     
# 示例列表
    score_list = [
    '''{"Pass":{"Agent1":True,"Agent2":False},"Score":{"Agent1":10,"Agent2":7}}''',
   
]



    evaluate_system_prompt=''' You are a code reviewer who is responsible for select a better solution from two agent's trajectories on sloving a code problem. 
The file and user query provided for each agent is same.
You should first think step by step to analyse whether the trajectory fulfills user's query, use Pass or Failed
After that, You should evaluate both solutions in the following dimensions：
Score this dimensions from 1-10, 1 means correct irrevlant code, 10 means excellent code
Reasoning Quality: Is the reasoning process correctly analyse the user input or code feedback? give a score between 1-10
Coda Quality: Evaluate The code correctness and whether it fulfill the user query? give a score between 1-10

Then you should give the total socre of each 
You should end your response with this sentence
Your final decsion must follow this json format use ``` ``` strictly:
```
{"Pass":{"Agent1":Pass/Failed,"Agent2":Pass/Failed},"Score":{"Agent1":score1,"Agent2":score2}}
```

Here is an example:
```
{"Pass":{"Agent1":Pass,"Agent2":Failed},"Score":{"Agent1":10,"Agent2":7}}
```

Notice: Both cv2.imwrite and plt.savefig is okay
'''
    user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
    chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)


    
    success=[]
    with open("gpt35_databench_trajectory.jsonl", 'r', encoding='utf-8') as file1, open("trajectory_llama30515_codeact_wo_plan.jsonl", 'r', encoding='utf-8') as file2:
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
            try:
                decision=rsp.split("```")[-2]
                print("Decision:\n",decision)
                success.append(decision)
                sum_scores(success)
                total_score = sum_scores(success)
                print(f"Agent 1 and Agent 2's total score sum is: {total_score}")
            except:
                continue

            
    print(success)
    
    sum_scores(success)
    