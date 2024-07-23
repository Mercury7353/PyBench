# 如果failed，则步数算10？
'''
计算NLPython Instruct 的 统计信息
条数
平均轮数分布
总token数
'''
import json

from collections import Counter
    
#model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B")
def read_lines(lines):
    data = []
    m = {}
    for line in lines:
        try:
            x = json.loads(line)
            m[x["index"]] = line
            data.append(x)
        except:
            pass
    data = sorted(data, key=lambda x: x["index"])
    lines = [json.dumps(item, ensure_ascii=False, indent=4) for item in data]
    return lines, m
def count_tokens(text):
    # 初始化tokenizer
    
    # 对文本进行编码，然后计算token数量
    tokens = tokenizer.encode(text, add_special_tokens=True)
    return len(tokens)



def read_jsonl(filename):
    file1 = open(filename)
    lines1 = file1.readlines()
    lines,_=read_lines(lines1)
    return lines


def save_jsonl(data, filename):
    with open(filename, "w") as f:
        for x in data:
            print(json.dumps(x, ensure_ascii=False), file=f)

def count_elements_in_intervals(elements):
    # 定义区间
    intervals = {'<=2': 0, '[4,6]': 0, '[7,9]': 0, '>=10': 0}

    for element in elements:
        if element <= 3:
            intervals['<=2'] += 1
        elif 4 <= element <= 6:
            intervals['[4,6]'] += 1
        elif 7 <= element <= 9:
            intervals['[7,9]'] += 1
        elif element >= 10:
            intervals['>=10'] += 1

    return intervals

import json

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def statistic_info(compare_path, solution_path):
    compare_data = read_jsonl(compare_path)
    solution_data = read_jsonl(solution_path)
    
    # 将solution_data转换为index到内容的映射，便于后续查找
    solution_dict = {}
    for line in solution_data:
        try:
            solution = json.loads(line)
            solution_dict[solution["index"]] = solution
        except:
            print("Error load")
            continue
    
    print("Length of Compare Data:", len(compare_data))
    
    turns_dis = []
    total_token_length = 0
    
    for line in compare_data:
        try:
            compare = json.loads(line)
            index = compare["index"]
        except:
            continue
        
        # 根据index找到对应的solution
        if index in solution_dict:
            solution = solution_dict[index]
            try:
                decision = compare["Decision"]["Pass"]["Agent2"]# 1 for 3.5 , 2 for anothers
                # 如果是failed，则步数直接置为10
                if decision == "Failed":
                    temp_len = 10
                else:
                    convs = solution["messages"]
                    temp_len = sum(1 for conv in convs if conv['role'] == 'assistant')
            except KeyError:
                print(f"Missing keys in data with index {index}")
                continue
        else:
            print(f"No matching solution found for index {index}")
            continue
        
        turns_dis.append(temp_len)
    
    # 假设这里的count_elements_in_intervals是之前定义好的，用于统计区间内元素的分布
    dis = count_elements_in_intervals(turns_dis)
    print("Distribution of turns:\n", dis)  
    print("Average turns:\n", sum(turns_dis) / len(compare_data))
   
    #print("Average token length:\n", total_token_length / len(compare_data) if compare_data else 0)

# 假设count_elements_in_intervals是一个已经定义好的函数，这里就不再实现它了



file_list=[("/data/zyl7353/codeinterpreterbenchmark/codeinterpreter_ultrachat_ablation.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codeinterpreter_ultrachat_ablation.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/codeinterpreter_cpt_jupyter.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codeinterpreter_cpt.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/Llama3_70b_Instruct0613.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_Llama3_70b_instruct_v1.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/codellama_70b_instruct.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codellama_70b_instruct.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/codellama34binstruct.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codellama34binstruct.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/deepseekcoder_33b.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_deepseekcoder33b_instruct.jsonl")]#file_list=["NLPython.jsonl"]
for paths in file_list:
    print("============================")
    compare_path,solution_path=paths[1],paths[0]
    print(solution_path,"\n")
    
    statistic_info(compare_path,solution_path)
    break
    #except:
        
        #print("Format Error")



    