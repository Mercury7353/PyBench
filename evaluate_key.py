import json
import signal
from fuzzywuzzy import fuzz

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

def load_json(file_path):
    answer = []
    with open(file_path, "r") as f:
        for line in f:
            try:
                line_dict = json.loads(line)
            except:
                continue
            answer.append(line_dict)
    return answer

def get_key(file_path):
    keys = []
    with open(file_path, "r") as f:
        for line in f:
            try:
                line_dict = json.loads(line)
            except:
                continue
            temp_dict = {}
            temp_dict["Decision"] = line_dict["Decision"]
            temp_dict['index'] = line_dict['index']
            keys.append(temp_dict)
    return keys

def find_best_match(long_string, key):
    key_length = len(key)
    best_match = ""
    highest_similarity = 0

    for i in range(len(long_string) - key_length + 1):
        window = long_string[i:i + key_length]
        similarity = fuzz.ratio(window, key)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = window

    return best_match, highest_similarity

def main():
    answer = load_json('/data/zyl7353/codeinterpreterbenchmark/gpt4_0524.jsonl')
    keys = get_key('/data/zyl7353/codeinterpreterbenchmark/extract_test_0619_v2.jsonl')

    total_keys = len(keys)
    total_score = 0

    # 设置超时处理器
    signal.signal(signal.SIGALRM, timeout_handler)

    # 读取answer和keys里面具有相同index的字典
    for key in keys:
        key_index = key['index']
        corresponding_answer = next((item for item in answer if item['index'] == key_index), None)
        decision = key["Decision"]["Keys"]
        print("Index",key_index)
        print("Keys",decision)
        #continue
        if not corresponding_answer:
            print(f'Failed: No matching answer for key with index {key_index}')
            continue
        try:
            trajectory = corresponding_answer["messages"]
        except:
            continue
        
        # 找到最后一个"content"键中含有<|execute_start|>的字典
        execute_start_index = -1
        for i in range(len(trajectory) - 1, 0, -1):
            if '<|execute_start|>' in trajectory[i]['content']:
                execute_start_index = i
                break
        
        #if execute_start_index == -1 or execute_start_index == 0:
            #print(f'Failed: No valid <|execute_start|> found for index {key_index}')
            #continue
        
        # 检查下一条字典的content键中是否不含"error"
        try:
            if 'error' in trajectory[execute_start_index + 1]['content'].lower():
                print(f'Failed: Error found after <|execute_start|> for index {key_index}')
                continue
        except:
            print(f'Failed: Error found after <|execute_start|> for index {key_index}')
            continue
        
        # 读取keys["Decision"]
        
        k = len(decision)
        score_per_decision_list = 1 / k
        trajectory_score = 0
        matched_snippets = []

        try:
            # 设置超时时间为20秒
            signal.alarm(20)
            for decision_list in decision:
                list_passed = False
                for element in decision_list:
                    for message in trajectory:
                        best_match, similarity = find_best_match(message['content'], element)
                        if similarity > 90:  # 设定相似度阈值为90
                            matched_snippets.append((element, best_match, similarity))
                            list_passed = True
                            break
                    if list_passed:
                        trajectory_score += score_per_decision_list
                        break
            signal.alarm(0)  # 取消超时计时器
        except TimeoutException:
            print(f'Timeout: Skipping index {key_index} due to timeout.')
            continue
        
        total_score += trajectory_score

        # 打印匹配的代码片段
        print(f'Matched snippets for index {key_index}:')
        for element, content, similarity in matched_snippets:
            print(f'Element: "{element}"')
            print(f'Matched Content: "{content}"')
            print(f'Similarity: {similarity}')
            print('-' * 40)
        print(f'Trajectory score for index {key_index}: {trajectory_score:.2f}')

    # 输出总得分
    print(f'Total score: {total_score:.2f}')

if __name__ == "__main__":
    main()
