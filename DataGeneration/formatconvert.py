'''
0318- convert the format of ai-user to functioncall format
"Code" for function
"Observation" for action
'''
import json
with open("output318v6.json") as f:
    data=json.load(f)
full_msg_dictlist=[]
msg_list=[]
for conv in data:
    if "Observation" in conv['content']:
        tool_msg={"role":"tool","content":conv['content'].replace("Observation","")}
        msg_list.append(tool_msg)
    elif conv['role']=='ai' and "Code:" in conv['content']:
        tool_msg={"role":"assistant","content":conv['content'].split("Code:")[-2],"tool_calls": [
          {
            "name": "excute_python",
            "arguments": {
              "code": conv['content'].split("Code:")[-1]
            }
          }
        ]
      }
        msg_list.append(tool_msg)
    else:
        msg_list.append(conv)
    
tool_dict= {   "tools": [
      {
        "name": "excuet_python",
        "description": "excuet the python code and get result",
        "parameters": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "The code is going to be excuted"
            },
          },
          "required": [
              "code"

          ]
        }
      }
    ]}
    
full_msg_dictlist.append({"messages":msg_list})
full_msg_dictlist.append(tool_dict)
full_msg_dictlist.append({"tool_choices":"auto"})
print(full_msg_dictlist)
with open("func_format_output.json",'w') as f:
    json.dump(full_msg_dictlist,f)