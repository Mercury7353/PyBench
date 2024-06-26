import json
count=0
index_list=[]
with open("/data/zyl7353/codeinterpreterbenchmark/compare_llama_gpt35_0601.jsonl",'r') as f:
    for line in f:
        json_dict=json.loads(line)
        PSR=json_dict['Decision']['Pass']
        if PSR['Agent2']=="Failed":
            index_list.append(int(json_dict['index']))
            count+=1
print(count/135.0)
# 使用 sorted() 函数进行升序排列
sorted_numbers = sorted(index_list)
print(sorted_numbers)