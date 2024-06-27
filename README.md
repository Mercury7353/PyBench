<h1 align="center"> PyBench: Evaluate LLM Agent on Real World Tasks </h1>

<p align="center">
<a href="comming soon">📃 Paper</a>
•
<a href="comming soon" >🤗 Data (PyInstruct)</a>
•
<a href="https://huggingface.co/Mercury7353/PyLlama3" >🤗 Model (PyLlama3)</a>
•
</p>  


PyBench is a comperhensive benchmark evaluting LLM on real world coding tasks including **chart data analysis**, **text data analysis**, **image/ audio editing** and **software / website development**.  
 We collect files from Kaggle, arXiv and another sources and automatically generate querys according to the type and content of each file.  

![Overview](images/hook.png)   




## Why we need PyBench?

The LLM Agent, equipped with a code interpreter, is capable of automatically solving real-world coding tasks, such as data analysis and image processing.
%
However, existing benchmarks primarily focus on either simplistic tasks, such as completing a few lines of code, or on extremely complex and specific tasks at the repository level, neither of which are representative of various daily coding tasks. 
%
To address this gap, we introduce **PyBench**, a benchmark that encompasses 6 main categories of real-world tasks, covering more than 10 types of files. 
![How PyBench Works](images/generateTraj.png)   

## 📁 PyInstruct

To figure outout a way enhacing model's ability on PyBench, we generate a homologous dataset: **PyInstruct**. The PyInstruct contains multi-turn interaction between model and files, stimulating models capility on coding, deugging and multi-turn complex task solving.  Compare to other Datasets focus on multi-turn coding ability, PyInstruct has longer turns and tokens per trajectory.  

![Data Statistics](images/data.png)
*Dataset Statistics. Token statistics are computed using Llama-2 tokenizer.*

## 🪄 PyLlama

We trained Llama3-8B-base on PyInstruct, CodeActInstruct, CodeFeedback and Jupyter Notebook Corpus to get PyLlama3, getting an outstandingly performance on PyBench


## 🚀 Evaluate your model on PyBench!

<video src="COMMING SOON"> </video>
*Demo of the chat interface.*

### Prepare the environment:
It is highly recommend to install these packages in a docker
```bash
pip install -r requirements.txt
```

### Set up your model
Use vllm to start a server in your local host, the default port is "8001"

run
```bash
bash SetUpModel.sh 
```
to start the server.
setup your model path and jinja template path.  

### Edit the config
Complete your model path and your port in ./config/model.yaml  

You can also explore the system prompt in this yaml




### Run on PyBench
Edit the output trajectory file path before run the code!
```bash
python /data/zyl7353/codeinterpreterbenchmark/inference.py --config_path ./config/<your config>.yaml --task_path ./data/meta/task.json --output_path <your trajectory.jsonl path>

```

### Run Unit test
      
- Step 1:
Put the output files in ./output   


- Step 2:
Set the trajectory path in ./data/unit_test/enter_point.py

- Step 3:
```bash
python data/unit_test/enter_point.py 
```


### 📊 LeaderBoard 

Please refer to [docs/EVALUATION.md](docs/EVALUATION.md) for detailed instruction.

## 📚 Citation

```bibtex
@inproceedings{wang2024executable,
      title={Executable Code Actions Elicit Better LLM Agents}, 
      author={Xingyao Wang and Yangyi Chen and Lifan Yuan and Yizhe Zhang and Yunzhu Li and Hao Peng and Heng Ji},
      year={2024},
      eprint={2402.01030},
      booktitle={ICML}
}
```
