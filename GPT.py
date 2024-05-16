'''
This file define the class to request GPT-3.5 or GPT-4
'''
import sys
sys.path.append("..")
from llmcenter0506 import LLMCenter
import requests
import os, sys
import json
import traceback
import time
import random
from tqdm import tqdm
import pdb
class GPT(LLMCenter):
    def __init__(self,model,temperature):
       
        llm_config={
                "app_code": 'CodeAndFunction',
                "user_token": '5T3QSU4H8FzMms69kqEO3A0zmhxm1S4bGkG_Nsm7m0Q',
                "token_url": 'https://llm-center.ali.modelbest.cn/llm/client/token/access_token',
                "url": 'https://llm-center.ali.modelbest.cn/llm/client/conv/accessLargeModel/sync',
                "model": model,
                "top_p": 0.9,
                "temperature": temperature,
            }
        
        super().__init__(llm_config=llm_config)
        self.name="GPT"

    