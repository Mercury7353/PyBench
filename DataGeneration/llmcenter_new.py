#!/usr/bin/env python
# encoding: utf-8
import requests
import os,sys
import json
import traceback
import time
import random
from tqdm import tqdm
import pdb


class ChatClient:
    def __init__(self, app_code='CodeAndFunction', user_token=None,model_id=20):
        self.app_code = app_code
        self.user_token = user_token
        self.app_token = self.get_app_token(app_code, user_token)
        self.model_id=model_id


    def get_app_token(self, app_code, user_token):
        res = requests.get(f'https://llm-center.ali.modelbest.cn/llm/client/token/access_token?appCode={app_code}&userToken={user_token}&expTime=3600')
        print(res.content)
        assert res.status_code == 200
        js = json.loads(res.content)

        #print("Let's print js\n",js)
        assert js['code'] == 0
        return js['data']

    def create_conversation(self, title='mm eval', user_id='x'):
        url = 'https://llm-center.ali.modelbest.cn/llm/client/conv/createConv'
        headers = {
            'app-code': self.app_code,
            'app-token': self.app_token,
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        data = {'title': title, 'type': 'conv', 'userId': user_id}
        try:
            js = requests.post(url, json=data, headers=headers)
            print(js.content)
            js = js.json()
            assert js['code'] == 0
            return js['data']
        except Exception as err:
            traceback.print_exc()
            print(err)
            time.sleep(1)
            self.app_token = self.get_app_token(self.app_code, self.user_token)
            return self.create_conversation(title, user_id)


    def chat_sync(self, system_prompt='You are a helpful assistant.', user_prompt='', conv_id=None):
        # TODO need to create new conversation for each eval?
        if conv_id is None:
            conv_id = self.create_conversation()

        url = 'https://llm-center.ali.modelbest.cn/llm/client/conv/submitMsgFreeChoiceProcess/sync'
        headers = {
            'app-code': self.app_code,
            'app-token': self.app_token,
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        data = {
            'convId': conv_id,
            'userSafe': 0, # disable user safe
            'aiSafe': 0,
            'modelId': self.model_id, # GPT-4 -> 15, gpt35 0613 32k -> 20, gpt4 0613 32k -> 25
            'sysPrompt': system_prompt,
            'generateType': "NORMAL",
            'userId': "panyinxu",
            'chatMessage': [
                {
                    "msgId": "",
                    "role": "USER", # USER / AI
                    "content": {"type": "TEXT", "pairs": user_prompt},
                    "parentMsgId": "",
                },
            ],
        }
        print('data\n', data)
        try:
            js = requests.post(url, json=data, headers=headers)
            print(js.content)
            js = js.json()
            assert js['code'] == 0
            return js['data']['content']
        except Exception as err:
            print(js)
            traceback.print_exc()
            print(err)
            time.sleep(1)
            self.app_token = self.get_app_token(self.app_code, self.user_token)
            conv_id = self.create_conversation()
            return self.chat_sync(conv_id, system_prompt, user_prompt)


def read_jsonl(filename):
    return [json.loads(line) for line in open(filename)]


def add_space(line):
    number = random.randint(0, 5)
    is_space = [True] * number + [False] * (len(line) - number)
    random.shuffle(is_space)
    new_line = ''
    for ch, flag in zip(line, is_space):
        if flag:
            new_line += ch + ' '
        else:
            new_line += ch
    return new_line


if __name__ == '__main__':
    user_token = "5U562TLXxNo9BMkoMAO6z0Y3p6Fc2yrgDX7G04_Ze3k"

    chat = ChatClient(app_code='CodeAndFunction', user_token=user_token)

    line = """请实现一个异步的函数，函数名为main，输入参数为Args，输出为Output，请续写代码，必要时可以引入一些依赖库
函数的作用是：计算输入参数的平方值，返回结果

from pydantic import BaseModel
from typing import List, Optional, Dict


class Args(BaseModel):
    input: int


class Output(BaseModel):
    result: int


async def main(args: Args) -> Output:"""
    res = chat.chat_sync(user_prompt=line)
    print(res)