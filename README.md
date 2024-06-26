# PyBench
PyBench is a comprehensive benchmark evaluating models ability in solving real-world coding tasks.


## Prepare the environment:
It is highly recommend to install these packages in a docker
```bash
pip install -r requirements.txt
```

## Set up your model
Use vllm to start a server in your local host, the default port is "8001"

run
```bash
bash SetUpModel.sh 
```
to start the server.
setup your model path and jinja template path.  

## Edit the config
Complete your model path and your port in ./config/model.yaml  

You can also explore the system prompt in this yaml




## Run on PyBench
Edit the output trajectory file path before run the code!
```bash
python /data/zyl7353/codeinterpreterbenchmark/inference.py --config_path ./config/<your config>.yaml --task_path ./data/meta/task.json --output_path <your trajectory.jsonl path>

```

## Run Unit test
      
### Step 1:
Put the output files in ./output   


### Step 2:
Set the trajectory path in ./data/unit_test/enter_point.py

### Step 3:
```bash
python data/unit_test/enter_point.py 
```


## Leaderboard
TBD