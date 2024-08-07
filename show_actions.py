# -*- coding: utf-8 -*-
import os
import string
import flask
import json
import time
from flask import Flask,stream_with_context,Response
from flask_cors import CORS
import requests
from typing import Iterable, List
### TODO
ROOT_PATH = "/home/ubuntu/MeKB"
### TODO

app = Flask(__name__)
CORS(app, supports_credentials=True)

def split2name_content(all_content):
  for index,c in enumerate(all_content):
    if c == ':':
      i = index
      break
  name = all_content[0:i]
  content = all_content[i+1:].strip()
  return name, content
    

@app.route("/get_actions", methods=["POST"])
def progress_1():
    actions_path = os.path.join(ROOT_PATH, 'actions')
    characters = ['Sheldon','Leonard','Penny','Howard','Raj','Amy']
    all_data = {}
    for name in characters:
        all_data[name] = []
        action_path = os.path.join(actions_path,f"{name}_actions.txt")
        if os.path.exists(action_path):
            f = open(action_path,'r',encoding='utf-8')
            r = f.readlines()
            f.close()
            chat_start = False
            for id,item in enumerate(r):
                line  = json.loads(item)
                if not isinstance(line,dict):
                    continue
                if item.startswith('\t'):
                    speaker, content = split2name_content(line['content'])
                    if not chat_start:
                        action = {'action':'chat','contents':[{'speaker': speaker, 'content':content}], 'time':line['time'], 'description':f"Talk to {line['person']} about '{line['topic']}'"}
                        chat_start = True
                    else:
                        action['contents'].append({'speaker': speaker, 'content':content})
                        
                    if id == len(r)-1 or not r[id+1].startswith('\t'):
                        all_data[name].append(action)
                else:
                    chat_start = False
                    all_data[name].append(line)
                
    return flask.jsonify({'response':all_data})


@app.route("/get_initdata", methods=["POST"])
def progress_2():
    profile_path = os.path.join(ROOT_PATH, "profile.json")
    long_memory_path = os.path.join(ROOT_PATH, "long-memory")
    story_path = os.path.join(ROOT_PATH, "The_big_bang_story.json")
    characters = ['Sheldon','Leonard','Penny','Howard','Raj','Amy']
    all_data = {}
    f = open(profile_path,'r',encoding='utf-8')
    profiles = json.load(f)
    f.close()
    for name in characters:
        for item in profiles:
            if item['name'] == name:
                f = open(os.path.join(long_memory_path,f"{name}.json"),'r',encoding='utf-8')
                memories = json.load(f)
                f.close()
                item['long_memory'] = memories
                all_data[name] = item
    
    f = open(story_path,'r',encoding='utf-8')
    stories = json.load(f)
    f.close()
    all_data['next_story'] = stories[-1]['text']
    return flask.jsonify({'response':all_data})


@app.route("/get_va", methods=["POST"])
def progress_3():
    va_path = os.path.join(ROOT_PATH, "va.json")
    f = open(va_path,'r',encoding='utf-8')
    va = json.load(f)
    f.close()
    return flask.jsonify({'response':va})
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7040, debug=False)  
