from typing import List, Dict, Any
import os
import json
import openai_async as openai
import requests
from agent.utils.llmExpends.BasicCaller import BasicCaller
from openai import OpenAI
import re


abs_path = os.path.dirname(os.path.realpath(__file__))

class GPT35Caller(BasicCaller):
    def __init__(self) -> None:
        self.model = "gpt-3.5-turbo"
        self.api_key = ""
        with open(os.path.join(abs_path, "..", "..", "..", "config", "api_key.json"), "r", encoding="utf-8") as api_file:
            api_keys = json.loads(api_file.read())
            self.api_key = api_keys["gpt-3.5"]
        if not self.api_key:
            raise ValueError("Api key not found")
    
    async def ask(self, prompt: str) -> str:
        counter = 0
        result = "{}"
        while counter < 3:
            try:
                
                ### TODO
                client = OpenAI(api_key = '', base_url = '')
                ### TODO

                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "user", "content": prompt},
                    ]
                )
                # print(completion.choices[0].message.content)
                result = completion.choices[0].message.content
                result = clean_text(result)
                
                if "```json" in result:
                    result = result.replace("```","")
                    result = result.replace("json","")
                    result = result.strip()
                try:
                    result = json.loads(result)
                except:
                    prompt_1 = f"Modify the following string so that it can be correctly parsed by the json.loads() method:\n{result}\n\nYou should just return the modified string."
                    result = json.loads(clean_text(GPTCall(prompt_1)))
                if isinstance(result, dict):
                    if "response" in result.keys():
                        result = result["response"]
                print(f"#############################\n{result}\n#############################")
                break


            except Exception as e:
                print(e)
                counter += 1
        return result
    
    def determine_ask(self, prompt: str) -> str:
        counter = 0
        result = "{}"
        while counter < 3:
            try:
                ### TODO
                client = OpenAI(api_key = '', base_url = '')
                ### TODO

                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "user", "content": prompt},
                    ]
                )
                print(completion.choices[0].message.content)
                result = completion.choices[0].message.content
                result = clean_text(result)
                
                if "```json" in result:
                    result = result.replace("```","")
                    result = result.replace("json","")
                    result = result.strip()
                try:
                    result = json.loads(result)
                except:
                    prompt_1 = f"Modify the following string so that it can be correctly parsed by the json.loads() method:\n{result}\n\nYou should just return the modified string."
                    result = json.loads(clean_text(GPTCall(prompt_1)))
                if isinstance(result, dict):
                    if "response" in result.keys():
                        result = result["response"]
                print(f"#############################\n{result}\n#############################")
                break


            except Exception as e:
                print(e)
                counter += 1
        return result

def clean_text(text):
    # Only keep json content
    pattern = r"```json(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        text =  match.group(1)
    
    # Remove some unexpected characters    
    punctuation_map = {
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "：": ":",
        "；": ";",
        "“": "\"",
        "”": "\"",
        "‘": "\'",
        "’": "\'",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "——": "-",
        "…": "...",
        "–": "-",
        "—": "-",
        "�": "."
    }
    pattern = r'[^a-zA-Z0-9\s\.,!?;:\'"\-({})\[\]]'
    for chinese, english in punctuation_map.items():
        text = text.replace(chinese, english)
    text = re.sub(pattern, '', text)
    text = text.strip()
    
    return text

def GPTCall(prompt):
    counter = 0
    result = "api调用失败"
    while counter < 3:
        try:
            ### TODO
            client = OpenAI(api_key = '', base_url = '')
            ### TODO
            completion = client.chat.completions.create(
                model="gpt-4o",
                # model = "gpt-3.5-turbo",
                # model="gpt-4-1106-preview",
                messages=[
                    {"role": "user", "content": prompt},
                ]
            )
            result = completion.choices[0].message.content
            print(f"%%%%%%%%%%%%%%%%%%%%%%%%\n{result}\n%%%%%%%%%%%%%%%%%%%%%%%")
            break
        
        except Exception as e:
            print(e)
            counter += 1
            
    return result