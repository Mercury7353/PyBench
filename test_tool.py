from langchain_experimental.tools.python.tool import PythonREPLTool
import traceback
import nbclient
import nbformat
from nbclient import NotebookClient
from nbclient.util import run_sync
import os
os.environ["JUPYTER_ALLOW_INSECURE_WRITES"]="1"
def _execute_code(code_str: str, tool: PythonREPLTool):
    """execute python code and return the execution result

    Args:
        code_str (str): the code to be executed
        tool (PythonAstREPLTool): python ast repl tool

    Returns:
        str: code execution result
    """
    # TODO: PythonAstREPLTool do not return full traceback when error occurs
    try:
        result = tool.invoke(code_str)
        result = str(result)
        return result
    except:
        return traceback.format_exc()

def execute_code(code_str: str,Kernel):
    #print("codeSTr",code_str)
    # 创建一个新的notebook对象
    #code_str = code_str.replace('\\n', '\n')
    
    # 添加一个包含代码的cell
    nb.cells.append(nbformat.v4.new_code_cell(code_str))
    
    total_cells=len(nb.cells)
    #print(total_cells)
    cell = nb.cells[-1]
    
    #nb_new=nbformat.v4.new_notebook()
    # 执行notebook
    
    client = NotebookClient(nb,allow_errors=True)
    client.kc=Kernel
    
    #client.execute()

    
    print(cell)
    print("Name",client.kc)
    outputs=nb.cells[-1]['outputs']#[0]['data']['text/plain']
    print("Output",outputs)
    
    try:
        client.reset_execution_trackers()
        client.execute_cell(cell=cell,cell_index=-1)
    except Exception as e:
        #print("Code error")
        traceback.print_exc()
        
        #error_message=traceback.format_exc()
        error_message=str(e)
        #split('Traceback')[-2]
        #error_message=error_message.split("\n")[-2]
        #print("Error",error_message)
        return error_message
    #"There are some errors in the code. All variable in this cell should be redefined,Please Debug:\n"+error_message
    
    # 提取执行结果
    #outputs = nb.cells[-1].outputs
    #print("CheckOutput",nb_c.cells[-1]['outputs'][0])
    outputs=nb.cells[-1]['outputs']#[0]['data']['text/plain']
    #print("Output",outputs)
    
    result = ""
    for output in outputs:
        #print("check point:",output.output_type)
        if output.output_type == "stream":  # 如果输出是标准输出或标准错误
            result += output.text
        elif output.output_type == "execute_result":  # 如果输出是执行结果
            result += str(output['data']['text/plain'])
        elif output.output_type == "error":  # 如果输出是错误
            result += "There are some errors in the code. All variable in this cell should be redefined,Please Debug:\n"
            result += "Error: " + str(output.ename) + "\n"
            result += str(output.evalue) + "\n"
            #result += "".join(output.traceback) + "\n"
            #roll_back(nb)
    #print(result)
    return result

tool=PythonREPLTool()
nb=nbformat.v4.new_notebook()
client = NotebookClient(nb,allow_errors=True)
client.km=client.create_kernel_manager()
print("Has kernel",client.km.has_kernel)
client.start_new_kernel()
print("Has kernel",client.km.has_kernel)
client.start_new_kernel_client()
Kernel=client.kc
   
#tool.execute()
rsp=execute_code("a=1\nprint(a)\nprint(1/0)",Kernel)
print(rsp)
rsp=execute_code("print(a)",Kernel)
print(rsp)
client._cleanup_kernel()