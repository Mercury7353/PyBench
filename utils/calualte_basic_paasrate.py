'''
只看最后一句有没有finished,计算pass rate
'''
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

def PassRate(compare_path, solution_path):
   #compare_data = read_jsonl(compare_path)
    solution_data = read_jsonl(solution_path)
    
    # 将solution_data转换为index到内容的映射，便于后续查找
    solution_dict = {}
    success_count=0
    for line in solution_data:
        try:
            solution = json.loads(line)
            solution_dict[solution["index"]] = solution
            if "Finish" in solution["messages"][-1]["content"]:
                success_count+=1
        except:
            print("Error load")
            continue
    
    print("Basic Success Rate:\n",success_count/143.0)
    



file_list=[("/data/zyl7353/codeinterpreterbenchmark/codeinterpreter_ultrachat_ablation.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codeinterpreter_ultrachat_ablation.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/codeinterpreter_cpt_jupyter.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codeinterpreter_cpt.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/Llama3_70b_Instruct0613.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_Llama3_70b_instruct_v1.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/codellama_70b_instruct.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codellama_70b_instruct.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/codellama34binstruct.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_codellama34binstruct.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/deepseekcoder_33b.jsonl","/data/zyl7353/codeinterpreterbenchmark/compare_deepseekcoder33b_instruct.jsonl"),
("/data/zyl7353/codeinterpreterbenchmark/codeinterpreter_3konly.jsonl","")
,("/data/zyl7353/codeinterpreterbenchmark/gpt35_0524.jsonl",""),
("/data/zyl7353/codeinterpreterbenchmark/gpt4_0524.jsonl",""),
("/data/zyl7353/codeinterpreterbenchmark/codact_llama2.jsonl",""),
("/data/zyl7353/codeinterpreterbenchmark/codeact_mistral.jsonl",""),
("/data/zyl7353/codeinterpreterbenchmark/codeqwen_chat_7B.jsonl",""),
("/data/zyl7353/codeinterpreterbenchmark/qwen2_7b_instruct.jsonl",""),
("/data/zyl7353/codeinterpreterbenchmark/glm_4_9b.jsonl","")]#file_list=["NLPython.jsonl"]
for paths in file_list:
    print("============================")
    compare_path,solution_path=paths[1],paths[0]
    print(solution_path,"\n")
    
    PassRate(compare_path,solution_path)
    
    #except
        
        #print("Format Error")



    