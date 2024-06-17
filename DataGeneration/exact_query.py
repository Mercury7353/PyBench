import pandas as pd
from llmcenter import ChatClient
import os

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

def generate_exact_query(file_path):
    chatbot=ChatClient()
    user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
    chatbot = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=20)

    task_list=["statistics description","simple data report","machine learning analysis on classification"
                                                  ,"machine learning analysis on clustering","time-series analyse","draw wordcloud","extract key words","theme analyse(LDA)"
                                                  ,"extract theme","Sentiment analysis","data visualization by line plot","data visualization by bar plot"
                                                  ,"data visualization by scatter plot","summary of the dataset","fliter the data","statistics description",
                                                  "a function to detect abnormal data"," Classification model","Clustering model",
                                                  "Time Series Analyse","Regression Model","Data Prediction","Key words",
                                                  "Theme Analyse","LDA Analyse","sentiment analysis","word cloud",
                                                  "bar plot","line plot","scatter plot","radar plot"]
    data=pd.read_csv(file_path)
    datainfo=data.iloc[0:3,:].to_string(index=False, col_space=100)
    #print("Data info :\n",datainfo)
    message=[{"role":"user","content":"simply describe the dataset:\n{datainfo}\n".format(datainfo=datainfo)}]
    description=chatbot.chat_sync(messages=message)
    message.append({"role":"ai","content":description})
    message.append({"role":"user","content":'''select a proper task from the task list and generatea a query(Describe by Neature Language.
                    You answer should follow this format:
                    Dataset Description: <decription>
                    Selected tasks:<list of task> is going to be combined to a high level query.
                    [Query]
                    <query>
                    [\Query] 
                    The task list(The task in the task list is just a guideline, you need to generate a complicate task according to the data description by yourself):\n{task_list}\n
                    Example 1:
                    Description: This data set is about house price in Boston, with columns of house price, house location,floor space
                    Selected tasks: [Draw a line plot, Train a regression model]
                    [Query]
                    Analyse how the floor space influence the house price by visualize the data and train a linear model
                    [\Query]
                    Example 2:
                    Description: This dataset is has only one columns, which is the titles of BBC news
                    Selected tasks:[Clean null values, LDA analyse]
                    [Query]
                    Excute LDA analysis on this news title dataset after preprocess.
                    [\Query]

                    Some Query example:
                    1. Run data analysis on sklearn Iris dataset, include a plot
                    2. Run data analysis on sklearn Wine recognition dataset, include a plot, and train a model to predict wine class with 20% as test set, and show prediction accuracy
                    3. This is a titanic passenger survival dataset, your goal is to predict passenger survival outcome. The target column is Survived. Perform data analysis, data preprocessing, feature engineering, and modeling to predict the target. Report accuracy on the eval data. 
                    
                    '''.format(task_list=task_list)})
    
    #print("Response:\n",description)
    query_raw=chatbot.chat_sync(messages=message)
    query_raw=query_raw.split("[Query]")[-1]
    query=query_raw.split("[\Query]")[0]

    print("QueryCheckPoint:\n",query)
    #print("CheckPoint",message)
    return query


    
if __name__ =="__main__":
    
    query_list=[]
    for file_name in os.listdir('/data/zyl7353/CodeInterpreter/dataset')[650:655]:# Select a file
        file_path='/data/zyl7353/CodeInterpreter/dataset/{}'.format(file_name)
        query_list.append(generate_exact_query(file_path,task_list))

    print(query_list)