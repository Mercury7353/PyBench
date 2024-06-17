'''
This file define the Code Reviewer CLass
Use GPT-3.5-turbo is enough?
The Code Review will focus on:
If not Error:
    If None Output:
        if plt.show():
            suggestion+= change to plt.save() and print img_path
        else:
            Check the query and code and reasoning what should be output
If Error:
    Track back error and give suggestions
'''
from llmcenter import ChatClient
user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"
chat = ChatClient(app_code="CodeAndFunction", user_token=user_token, model_id=20)

class Codereviewer():
    def __init__(self):
        self.query=''
        self.code=''
        self.obs=''
        self.CodePassport=False
        self.CodeSuggestion=''
    
    def check(self,question,code,CodeResult):
        self.query=question
        self.code=code
        self.obs=CodeResult
        #print("breakpoint ",CodeResult)
        if "error" in str(CodeResult):
            #print("CodeError",self.obs)
            #raise "AAAAAAAAAAAAstop!!!"
            self.CodeSuggestion=chat.chat_sync(messages=[{'role':"user","content":"You are a code reviewer, the code has some errors, Please give instruction to modify the code. Code:{0},\n Error:{1}".format(self.code,self.obs)}])
        else:
            
            if CodeResult==None or len(str(CodeResult))==0:
                
                if "plt.show" in code and "plt.savefig" not in code:
                    self.CodeSuggestion="You should use plt.savefig()  instead of plt.show() to save the image and print the path you save it"

                elif "print" not in code:
                    print("None Output")
                    self.CodePassport=True
                    self.CodeSuggestion="You should use print(), to report what you have done. If you draw a image, you should write :print('The image is saved to'+file_path)"
                    #chat.chat_sync(messages=[{'role':"user","content":"You are a code reviewer, the code should print and show the solution to the query (like the report of work). Please give instruction to modify the code. Just Give suggestions. Not Give CodeQuery:{0} \n,Code:{1} ".format(self.query,self.code)}])

            else:
                self.CodePassport=True
        return self.CodePassport,self.CodeSuggestion



