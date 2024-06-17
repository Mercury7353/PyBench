import pandas as pd
from llmcenter import ChatClient
import os
import random
import traceback
'''
This file define a class that generate the query exactly related to the dataset.
Enhancing the quality of generated data
parameter: file_path
Step1:pd.readcsv(file_path)\n data.head()
Step2:get infomation and pass it to LLM(gpt-3.5-turbo)  
Step3:Given task lists , return specific task
task list=["data cleaning","data mining","data integreter","statistics description","simple data report","machine learning analysis on classification"
                                                  ,"machine learning analysis on clustering","time-series analyse","draw wordcloud","extract key words","theme analyse(LDA)"
                                                  ,"extract theme","Sentiment analysis","data visualization by line plot","data visualization by bar plot"
                                                  ,"data visualization by scatter plot","summary of the dataset","Cleaning the duplicated data",
                                                  "remove null data","remove outlier data","sort the data","fliter the data","statistics description",
                                                  "a function to detect abnormal data"," Classification model","Clustering model",
                                                  "Time Series Analyse","Regression Model","Data Prediction","Key words",
                                                  "Theme Analyse","LDA Analyse","sentiment analysis","word cloud",
                                                  "bar plot","line plot","scatter plot","radar plot"]

问题:经常选择单一的query,而且query不具体 解决：写example，使得更加具体
'''
def get_random_samples(input_list, num_samples):
    """
    从列表中随机抽取指定数量的元素。

    参数:
    input_list (list): 输入列表。
    num_samples (int): 要抽取的元素数量。

    返回:
    list: 随机抽取的元素列表。
    """
    if num_samples > len(input_list):
        raise ValueError("num_samples cannot be greater than the length of the input list.")
    
    return random.sample(input_list, num_samples)

import fitz

def get_first_500_chars(file_path):
    """
    获取 PDF 或 TXT 文件的前 500 个字符。

    参数:
    file_path (str): 文件路径。
    file_type (str): 文件类型，'pdf' 或 'txt'。

    返回:
    str: 文件的前 500 个字符。
    """
    
    def get_pdf_first_500_chars(file_path):
        doc = fitz.open(file_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
            if len(text) >= 500:
                break
        return text[:500]

    def get_txt_first_500_chars(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read(500)
        return text

    if 'pdf' in file_path:
        return get_pdf_first_500_chars(file_path)
    elif 'txt' in file_path:
        return get_txt_first_500_chars(file_path)
    else:
        raise ValueError("Unsupported file type. Use 'pdf' or 'txt'.")




def generate_exact_query(file_path):
    #chatbot=ChatClient()
    user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
    chatbot = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=106)

    task_list=["LDA Analyse","WordCloud","Extract Key words","Sentiment Analyse","Summary Main idea(Just Read few thousand words of the content directly and make summary)","Content Based QA"]
    #data=pd.read_csv(file_path)
    current_task_list=get_random_samples(task_list,3)
    #datainfo=data.iloc[0:3,:].to_string(index=False, col_space=100)
    try:
        datainfo=get_first_500_chars(file_path)
    except:
        traceback.print_exc()
        return ""
    #print("Data info :\n",datainfo)
    message=[{"role":"user","content":"simply describe the text file:\n{datainfo}\n".format(datainfo=datainfo)}]
    description=chatbot.chat_sync(messages=message)
    #messages=[]
    message.append({"role":"ai","content":"The description for the text file is:{}".format(description)})
    message.append({"role":"user","content":'''select proper tasks from the task list and generatea a query(Describe by Neature Language.
                    You should give a query no more than one sentence!
                    You answer should follow this format:
                    Dataset Description: <decription>
                    Selected tasks:[Select Only one high-level task] is going to be combined to a high level query.
                    [Query]
                    <query>
                    [\Query] 
                    The task list(The task in the task list is just a guideline, you need to generate a complicate task according to the data description by yourself):\n{task_list}\n
                    
                    Examples:
                    这篇文章的核心观点是什么？
                    根据这篇文本，总结核心内容，写一个网站
                    Extract the keywords from content of the news and draw a wordcloud
                    Apply a LDA analyse on the dataset
                    Excute Sentiment Analyse on the given csv file
                    ...


                    '''.format(task_list=current_task_list)})
    
    #print("Response:\n",description)
    query_raw=chatbot.chat_sync(messages=message)
    query_raw=query_raw.split("[Query]")[-1]
    query=query_raw.split("[\Query]")[0]

    print("QueryCheckPoint:\n",query)
    #print("CheckPoint",message)
    return query


    
if __name__ =="__main__":
    
    query_list=[]
    for file_name in os.listdir('/data/zyl7353/ReAct/TextData/arxivpapers'):# Select a file
        file_path='/data/zyl7353/ReAct/TextData/arxivpapers/{}'.format(file_name)
        print(file_path)
        query_list.append(generate_exact_query(file_path))
        

    print(query_list)