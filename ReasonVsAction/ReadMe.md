# Reasoning vs CodeAction
通过实验定量探究 Agent 的ReAct过程中哪个更重要？  
## Method:  
Trajectory1: GPT Reasoning + Llama3 code  
Trajectory2: Llama3 Reasoning + GPT code  

## Metric : GPT evaluate Pass Rate & Win Rate  


- Notice: 续写的时候直接把<|execute_start|>给llama3，以直接续写，不再reasoning