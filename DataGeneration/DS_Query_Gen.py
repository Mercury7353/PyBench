'''
This file utilize GPT-4 to generate DAG for data science
'''

'''
Log: I should complete the file_path function

Initial Input:(system message) Dataset Description and file path
User: Specific Task
Assistant: Code and solution
User: Response & New Task
...
User: Final Task
Assistant: Final response
Like CAMEL? 
自己写吧 CAMel 没法follow tasks sequence
Output Response
Feed
'''
from llmcenter_new import ChatClient
import networkx as nx
import matplotlib.pyplot as plt

def draw_DAG(DAG):
    # 创建有向图
    G = nx.DiGraph()
    # 添加节点和边
    for task in DAG:
        G.add_node(task["task_id"], instruction=task["instruction"])
        for dependency in task["dependent_task_ids"]:
            G.add_edge(dependency, task["task_id"])

    # 绘制图形
    pos = nx.spring_layout(G)  # 为了美观，使用spring布局
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10, font_weight='bold')

    # 如果你想显示task的说明作为标签
    task_labels = nx.get_node_attributes(G, 'task_id')
    nx.draw_networkx_labels(G, pos, labels=task_labels)

    plt.show()
user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"

chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=36)
def Generate_DAG():
    DAG_template='''
    [
    {
    "task_id": "1",
    "dependent_task_ids": [],
    "instruction": "Conduct data exploration on the dataset to understand its structure, missing values, and basic statistics."
    },
    {
    "task_id": "2",
    "dependent_task_ids": ["1"],
    "instruction": "Perform correlation analysis and causal inferences to identify relationships between variables."
    },
    {
    "task_id": "3",
    "dependent_task_ids": ["1"],
    "instruction": "Select proper images to visualize the data"
    },
    {
    "task_id": "4",
    "dependent_task_ids": ["2", "3"],
    "instruction": "Carry out feature engineering to prepare the dataset for predictive modeling."
    }
    ]
    '''
    #draw_DAG(eval(DAG_template))
    Query={"role":"user","content":'''

    You are a Data scientist and a leader of a data science group. You are familiar with the entire pipeline of DataScience, including
    data preprocessing, data visualization, data mining, machine learning, and write a data analysis report. 
    Your task is to manage the sequence of tasks reasonablely. Thus, you should decompose the DataScience area into some specific tasks, which has a DAG structure.
    There is a simple example:
    ```
    {}
    ```
    Strictly follow the format of the template but I need a more comprehensive DAG structure. At least 10 various tasks.
    For instance, you DAG should contain tasks from these topics:
    1. a quick explain on the data
    2. summary key information of data
    3. standardizing the data
    4. Data cleaning to eliminate outliers, missing values or duplicates
    5. Data Visualization
    6. utilize simple machine learning models to predict
           
    Only return the json
    '''.format(DAG_template)}


    for i in range(3):
        try:
            DAG=chat.chat_sync(user_prompt=Query)
            #print("DAG:",DAG)
            #print("END DAG")
            DAG=DAG.split("```")[-2]
            DAG=DAG.replace("json","")
            #draw_DAG(eval(DAG))
            break
        except:
            print("DAG format error:Retry")
            print(DAG)
            continue
    return DAG

def Generate_task_sequence(DAG):
    
    # Step2: Give a description of Dataset, select a path of tasks from DAG
    # Q: how to generate the description? 
    # Generate specific query
    Query_2=[{"role":"system","content":'''
            You are a Data scientist and a leader of a data science group. 
    Your task is to manage the sequence of tasks reasonablely. The first task must be make a brief summary on the dataset
    This is your DAG, you should select tasks from it and manage them wisely. 
    {}
    '''.format(DAG)
    },
    {"role":"user","content":'''
    Task: Select tasks form your DAG and make a task sequence. The task you select should be linked as a path in DAG. The task you select should contains different topics like data mining,data visualization or machine learning.Example output: [1,3,4,5,6,7]. Only return the list. Notice that the length of list should about 5. Check if your task list is a chain in DAG'''}]
    #print(Query_2)
    Task_sequence=chat.chat_sync(messages=Query_2,temperature=0.6)
    print(Task_sequence)
    task_list=eval(Task_sequence)
    task_description_list=[]
    for task_id in task_list:
        for task in eval(DAG):
            if str(task_id)==task['task_id']:
                task_description_list.append(task["instruction"])

    return task_description_list


