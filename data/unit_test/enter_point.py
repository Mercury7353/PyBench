import importlib
import os  
import tests
import traceback
import json

def check_content(task_id,trajectory):
    '''
    根据task_id匹配并运行相应的单元测试函数。
    '''
    # 构建测试函数的名称
    test_function_name = f'test_task_{task_id}'
    if not test_function_name:
        print(f"No tests found for task_id {task_id}")
        return
    
    
    unit_test=getattr(tests, test_function_name)
    unit_test(trajectory)

# 示例调用
if __name__=="__main__":
    result_map={}
    trajectory_map={}
    trajectory_path="/data/zyl7353/codeinterpreterbenchmark/unit_test_result/CodeQwen1.5-7B-Chat/trajectory.jsonl"# The Path of trajectory data
    
    result_path="/data/zyl7353/codeinterpreterbenchmark/result.jsonl" # The path to save result
    with open(trajectory_path,"r") as f:
        for line in f:
            json_dict=json.loads(line)
            try:
                trajectory_map[json_dict["index"]]=json_dict['messages']
            except:
                trajectory_map[json_dict["index"]]=[{"role":"","content":"error"}]
    Pass_Count=0
    #check_content(1)  # 运行所有 test_task_1_ 开头的测试函数
    for i in range(2,153):
        try:
            check_content(i,trajectory_map[str(i)]) 
            print(i,"Pass")
            result_map[str(i)]="Pass"
            Pass_Count+=1
        except:
            traceback.print_exc()
            result_map[str(i)]="Failed"
            print(i,"Failed")

    print(Pass_Count)
    print("PassRate:",float(Pass_Count)/143.0)
    with open(result_path,"w") as f:
        json_string=json.dumps(result_map)
        f.write(json_string)
    
