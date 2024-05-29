from __future__ import annotations



from utils.llama3 import LlaMa3
from utils.my_chat_interface import MyChatInterface

system_prompt = """You are an AI Agent who is proficient in solve complicated task. 
  Each step you should wirte executable code to fulfill user query. Any Response without code means the task is completed and you do not have another chance to submit code

  You are equipped with a codeinterpreter. You can give the code and get the execution result of your code. You should use the codeinterpreter in the following format: 
  <|execute_start|>
  ```python  

  <your code>  

  ``` 
  <|execute_end|>


  WARNING:Do not use cv2.waitKey(0) cv2.destroyAllWindows()!!! Or the program will be destoried

  Each round, your answer should ALWAYS use the following format(Each of your response should contain code, until you complete the task):


  Analyse:(Analyse the message you received and plan what you should do)  

  This Step Todo: One Subtask need to be done at this step  

  Code(WARNING:MAKE SURE YOU CODE FOLLOW THE FORMAT AND WRITE CODE OR THE TASK WILL BE FAILED): 
  <|execute_start|>
  ```python  

  <your code>


  ```  
  <|execute_end|>


  You will got the result of your code after each step. When the code of previous subtask is excuted successfully, you can write and excuet the code for next subtask
  When all the code your write are executed and you got the code result that can fulfill the user query, you should summarize the previous analyse process and make a formal response to user, The response should follow this format:
  WARNING:MAKE SURE YOU GET THE CODE EXECUTED RESULT THAT FULFILLED ALL REQUIREMENT OF USER BEFORE USE "Finished"
  Finished: <Answer to user query>

  Some notice:
  1. When you want to draw a plot, use plt.savefig() and print the image path in markdown format instead of plt.show()
  2. Save anything to current folder
  3. End the process whenever you complete the task, When you do not have Action(Code), Use: Finished: <summary the analyse process and make response>
  4. Do not ask for user input in your python code.  
"""


LLM = LlaMa3(tools=None)


def chat(message, chat_history):
    print("message:", message)
    print("history:", chat_history)

    def history_to_messages(message, history):
        global system_prompt
        messages = [{"role": "system", "content": system_prompt}]
        for user_msg, assistant_msg in history:
            if user_msg is not None:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg is not None:
                messages.append({"role": "assistant", "content": assistant_msg})
        if isinstance(message, str):
            messages.append({"role": "user", "content": message})
        elif isinstance(message, dict):
            if "files" in message:
                filepath = ",".join(message["files"])
                if filepath.strip() != "":
                    messages.append(
                        {
                            "role": "user",
                            "content": f"[INFO]The data is uploaded to {filepath}",
                        }
                    )
                messages.append({"role": "user", "content": message["text"]})
            else:
                messages.append({"role": "user", "content": message["text"]})
        return messages

    messages = history_to_messages(message, chat_history)
    print("converted messages:", messages)
    response = LLM.chat(messages=messages)
    print("get response:", response)
    return response


demo = MyChatInterface(
    fn=chat,
    examples=[
        {"text": "draw a cute cat for me"},
        {"text": "make a qrcode which links to www.modelbest.cn"},
        {"text": "2的1000次方是多少？"},
    ],
    title="CPMInterpreter",
    multimodal=True,
)

if __name__ == "__main__":
    demo.launch(share=True, allowed_paths=["."])
