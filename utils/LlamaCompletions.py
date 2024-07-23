from openai import OpenAI
from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2 import Template

class LlamaCompletion():
    def __init__(self) -> None:
        self.client=OpenAI(
            base_url="http://localhost:8001/v1",
            api_key="token-abc123",
        )
        
        self.model ="/data/zyl7353/models/codeinterpreter_0529-hf"
        
        self.template=Template('''{% for message in messages %}{{'<|begin_of_text|>' + message['role'] + '\n' + message['content']}}{% if (loop.last and add_generation_prompt) or not loop.last %}{{ '<|end_of_text|>' + '\n'}}{% endif %}{% endfor %}
{% if add_generation_prompt and messages[-1]['role'] != 'assistant' %}{{ '<|begin_of_text|>assistant\n' }}{% endif %}''')
       
        
        
    def chat(self,messages):
        message_string=self.format_message(messages)
        
        message_string=message_string.rsplit("<|execute_start|>",1)[0]+"<|execute_start|>"
        
        #message_string+="\n<|begin_of_text|>assistant\n"
        print(message_string)
        print("----=====================-----\n")
        completion = self.client.completions.create(
        model=self.model,
        prompt=message_string,
        max_tokens=8192,
        echo=False,
        stream=False,
        temperature=0.2
        )
        ans=""
        for choice in completion.choices:
            print(choice.text)
            ans+=choice.text.strip()
            
        return ans
    
    def format_message(self,messages):
        rendered = self.template.render(messages=messages, add_generation_prompt=True)
        return rendered
        

if __name__=="__main__":
    L=LlamaCompletion()
    rsp=L.chat([{"role":"system","content":"you are a helpful assistant"},{"role":"user","content":"Analyse the dataset"},{"role":"assistant","content":"Analyse: I'am going to write python code to load the dataset at ./data.csv.\n<|execute_start|>\n"}])
    print(rsp)

