from assistant import GPT
import os 
import json
os.environ["AZURE_OPENAI_API_KEY"]="b5ceeca154844f009e4d6618188305d3"
os.environ['AZURE_OPENAI_ENDPOINT']="https://zyl-code-interpreter.openai.azure.com/"

#My_Assistant=GPT()
#My_Assistant.chat("Clean the null values and draw a bar plot for me","./Visualization/radar.csv")

with open("task.json") as f:
    json_string=f.read()
    tasks=json.loads(json_string)



for task in tasks:
    index=task["index"]
    task_name=task['user']
    file_path=task['file_path']
    if "and" in file_path:
        file_list=file_path.split(" and ")

    else:

        file_list=[file_path]
    file_path="./0.csv"
    file_list=[file_path]
    task_name="First, clean the data, drop the nan value and outliers. Then train a machine model to predict Sales"
    My_Assistant=GPT()
    My_Assistant.chat(task_name,file_list,index)
    break
    
    