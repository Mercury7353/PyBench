# quickstart
1. setup environment
```
conda create -n codeinterpreter python==3.11
conda activate codeinterpreter
pip install -r requirements.txt
```
2. run the code
```
python run_code_interpreter.py config/gpt35_prompt_v2.yaml data/meta/task.json gpt35_prompt_result.jsonl
```
3. check the result

The output files locate in the output folder. The ipynb files locate in cells folder. Run the following commands to visualize the results.

```
jupyter-notebook cells
```

4. evaluate the result
```
python eval_code_interpreter.py
```