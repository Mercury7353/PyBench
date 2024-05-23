import json
from glob import glob
import pandas as pd


def find_fuzzy_file(file_name, row_idx):
    files = []
    
    if isinstance(file_name, str):
        file_name = file_name.replace("📄", "")
        for file in glob(f"../data/{file_name}.*"):
            files.append(file)
    for file in glob(f"../data/{row_idx}.*"):
        files.append(file)
    return files


df = pd.read_excel("../data/meta/工具学习能力分类.xlsx")
data = []
category1, category2, category3 = None, None, None
"""
                    能力大项  能力分项   具体能力                                               附带文件                                      system prompt                                                 问题  Unnamed: 6 Unnamed: 7
0  简单数据分析处理\n（pandas）  数据清洗  去除重复项                           📄yearly_deaths_by_clinic  You are a proficient Data Scientist who good a...  Could you help me clean the given dataset? Esp...         NaN        NaN
1                 NaN   NaN    NaN  📄Week 40 - US Christmas Tree Sales - 2010 to 2016  You are a proficient Data Scientist who good a...                                   帮我处理一下这个数据里面的重复值         NaN        NaN
2                 NaN   NaN   去除空值                             📄accessories_organizer  You are a proficient Data Scientist who good a...                    Let's get rid of the null value         NaN        NaN
3                 NaN   NaN    NaN       📄ThrowbackDataThursday - 202001 - Ozone Hole  You are a proficient Data Scientist who good a...                        请帮我做一下简单的数据预处理，检查空值，重复值和异常值         NaN        NaN
4                 NaN   NaN  去除异常值                                    📄activity_clean  You are a proficient Data Scientist who good a...             Please detect and handle with outliers         NaN        NaN
"""
for i, row in df.iterrows():
    # print(row.to_dict())
    if isinstance(row["能力大项"], str) and row["能力大项"].strip() != "":
        category1 = row["能力大项"]
    if isinstance(row["能力分项"], str) and row["能力分项"].strip() != "":
        category2 = row["能力分项"]
    if isinstance(row["具体能力"], str) and row["具体能力"].strip() != "":
        category3 = row["具体能力"]
    question = row["问题"]
    if not isinstance(question, str) or question.strip() == "":
        attach = row["附带文件"]
        files = find_fuzzy_file(attach, i + 2)
        if isinstance(attach, str):
            data[-1]["attachments"].append(attach)
        data[-1]["file_paths"] += files
    else:
        attach = row["附带文件"]
        files = find_fuzzy_file(attach, i + 2)
        data.append(
            {
                "index": str(i + 2),
                "category1": category1,
                "category2": category2,
                "category3": category3,
                "user": question,
                "file_paths": files,
                "attachments": [],
            }
        )
        if isinstance(attach, str):
            data[-1]["attachments"].append(attach)
json.dump(data, open("../data/meta/task.json", "w"), ensure_ascii=False, indent=4)
