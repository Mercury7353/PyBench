# PyBench

## Set up your model
use vllm to set up your model,
edit the model path in yaml file 


## Run on PyBench
Edit the output trajectory file path before run the code!
```bash
bash test_llama3_beta.sh

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


