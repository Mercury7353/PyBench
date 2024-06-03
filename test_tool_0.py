import json
import jsonlines
with open("./llama3_0530_beta_v0.jsonl",'r') as f:
    json_str=f.read()
    with jsonlines.Reader(json_str.splitlines()) as reader:
        print(json_str[10520:10527])
        a=[obj['index'] for obj in reader ]
        print(a)
        for obj in reader:
            print(obj['index'])
            break