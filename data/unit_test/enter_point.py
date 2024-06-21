# The enter point for unit tests  
'''

1.  先检测文件有没有  btw 有些并不要求文件输出啊 ?
2.  然后检测文件是不是匹配

'''
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
    trajectory_map={}
    with open("/data/zyl7353/codeinterpreterbenchmark/test_0620.jsonl","r") as f:
        for line in f:
            json_dict=json.loads(line)
            trajectory_map[json_dict["index"]]=json_dict['messages']
    
    #check_content(1)  # 运行所有 test_task_1_ 开头的测试函数
    for i in range(2,70):
        try:
            check_content(i,trajectory_map[str(i)])  # 运行所有 test_task_2_ 开头的测试函数
            print(i,"Pass")
        except:
            #traceback.print_exc()
            print(i,"Failed")









