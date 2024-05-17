from openai import OpenAI
# 首先把tool_dict 整合到system message里面
from tooltransform import my_input_format
from tooltransform import message_format
class LlaMa3():
    def __init__(self,tools) -> None:
        self.client= OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="token-abc123",
)
        self.tools=tools
        self.name="Llama3"

    def chat(self,messages):
        result=my_input_format(messages,tools=self.tools,tool_choice=None,output=None)
        completion = self.client.chat.completions.create(
                      model="/home/jeeves/zyl/zyl7353/CodeInterpreter/ObjLLaMa/codeinterpreter_codeact_0515_hf",
                      messages=result,
                      temperature=0.2,
                    )
        
        #content=completion.choices[0].message['content']['content']
        #print("test",content)

        return completion.choices[0].message.content
#client =
'''
messages=[
    {"role": "system", "content": "你是一个AI助手"},
    {"role":"user","content":"帮我计算1+1"},
    {"role":"assistant","content":"好的，我会调用excute_python工具\n","tool_calls": [
          {
            "name": "excute_python",
            "arguments": {
              "code": "print(1+1)"
            }
          }
        ]}, # 如果有tool calls，那么拼接 <|tool_call|>
    {"role":"tool","content":"2"},
    {"role":"user","content":"帮我计算1+1"}
    # {"role":"user","content":"请调用excute_python工具，计算1+10"}
  ]
#new_messages=[]

#for msg in messages:
#    rsp=message_format(msg)
#    print("rsp",rsp)
#    new_messages.append(rsp)
tools= [
      {
        "name": "excute_python",
        "description": "excute the python code and get result",
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
    ]

result=my_input_format(messages=messages,tools=tools,tool_choice=None,output=None)
print(result)
for msg in result:
    
    print("tool_call_string" in msg.keys())
'''

