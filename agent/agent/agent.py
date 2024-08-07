from typing import List, Dict, Any

from agent.agent.components.memory_store import MemoryData
from agent.agent.components.state import State
from agent.agent.components.cache import Cache
from agent.agent.components.prompt import Prompts
from agent.agent.components.controller import Controller
from agent.utils.llm import LLMCaller

import re
import os
import json
import datetime
import faiss
import numpy as np
import requests
abs_path = os.path.dirname(os.path.realpath(__file__))
### TODO
ROOT_PATH = "D:\WorkFolder\Mekb-sim"
### TODO


class Agent:
    def __init__(self, name: str, bio: str, goal: str, model: str, memorySystem: str, planSystem: str, buildings: List[str], cash: int, start_time: float) -> None:
        self.memory_data = MemoryData()
        self.state = State()
        self.start_time = datetime.datetime.fromtimestamp(start_time / 1000)
        self.state.buildings = buildings
        self.state.cash = cash
        self.cache = Cache()
        self.name = name
        self.bio = bio
        self.goal = goal
        if model:
            self.caller = LLMCaller(model)
        self.prompt_log_path = os.path.join(ROOT_PATH, "logs", f"{name}_prompt.txt")
        self.actions_log_path = os.path.join(ROOT_PATH, "actions", f"{name}_actions.txt")
        if os.path.exists(self.actions_log_path):
            os.remove(self.actions_log_path)
        self.prompts = Prompts()
        self.controller = Controller(memorySystem, planSystem)
        self.profile = self.get_profile(self.name)
        self.chat_cnt = 0
    
    def log_prompt(self, input: Any):
        if not isinstance(input, str):
            input = json.dumps(input, ensure_ascii=False, separators=(",", ":"))
        with open(self.prompt_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{input}\n")
    
    def log_actions(self, action: Dict[str, Any]): 
        log_file = open(self.actions_log_path, "a", encoding="utf-8")
        if action['action'] == 'chat':
            if len(action['chats']) == 0 or len(action['chats']) == 1: 
                if len(action['chats']) == 0: 
                    item = {}
                    item['person'] = action['person']
                    item['topic'] = action['topic']
                    item['time'] = action['time']
                    item['speaker'] = action['speaker']
                    item['content'] = action['reply']['content']
                    input = '\t' + json.dumps(item, ensure_ascii=False)
                    log_file.write(f"{input}\n")
                else: 
                    item = action['chats'][0]
                    item['person'] = action['person']
                    item['topic'] = action['topic']
                    item['time'] = action['time']
                    item['speaker'] = action['speaker']
                    input = '\t' + json.dumps(action['chats'][0], ensure_ascii=False)
                    log_file.write(f"{input}\n")
                    item = {}
                    item['person'] = action['person']
                    item['topic'] = action['topic']
                    item['time'] = action['time']
                    item['speaker'] = action['speaker']
                    item['content'] = action['reply']['content']
                    input = '\t' + json.dumps(item, ensure_ascii=False)
                    log_file.write(f"{input}\n")
            else:  
                item = action['chats'][-1]
                if isinstance(item, dict):
                  item['person'] = action['person']
                  item['topic'] = action['topic']
                  item['time'] = action['time']
                  item['speaker'] = action['speaker']       
                  input = '\t' + json.dumps(action['chats'][-1], ensure_ascii=False)
                  log_file.write(f"{input}\n")
                if isinstance(item, str):
                  try:
                    item = json.loads(item)
                    item['person'] = action['person']
                    item['topic'] = action['topic']
                    item['time'] = action['time']
                    item['speaker'] = action['speaker']       
                    input = '\t' + json.dumps(action['chats'][-1], ensure_ascii=False)
                    log_file.write(f"{input}\n")
                  except:
                    pass
                item = {}
                item['person'] = action['person']
                item['topic'] = action['topic']
                item['time'] = action['time']
                item['speaker'] = action['speaker']
                item['content'] = action['reply']['content']
                input = '\t' + json.dumps(item, ensure_ascii=False)
                log_file.write(f"{input}\n")
        
        if action['action'] == 'move':
            move_info = {'action':'move', 'description':f"Go to {action['building']} for '{action['purpose']}'", 'time':action['time']}
            input = json.dumps(move_info, ensure_ascii=False)
            log_file.write(f"{input}\n")
            
        if action['action'] == 'use':
            use_info = {'action':'use', 'description':action['operation'], 'time':action['time']}
            input = json.dumps(use_info, ensure_ascii=False)
            log_file.write(f"{input}\n")
            
        
        log_file.close()

    async def plan(self) -> None:
        # QAFramework Experience
        buildings = {"Sheldon":["Sheldon and Leonard's apartment"],
                     "Leonard":["University Physics Department Office"],
                     "Penny":["University Physics Department Office"],
                     "Raj":["Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Howard":["Amy's house","Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Amy":["Sheldon and Leonard's apartment"]}
        if self.controller.planSystem == "QAFramework":
            await self._qa_framework() 
        game_time = self.get_game_time()
        self.state.plan_prompt = self.prompts.get_text("plan", {
            "{profile}": self.profile,
            "{time}": game_time,
            "{plan_cache}": self.cache.plan_cache,
            "{memory_1}": self.memory_data.get_impression_memory(),
            "{memory_2}": self.cache.chat_cache,
            "{buildings}": buildings[self.name],
            "{question}": self.state.question,
            "{answer}": self.state.answer,
        })
        self.log_prompt(self.state.plan_prompt)
        # {"building": "xxx", "purpose": "xxx"}
        
        self.state.plan =  await self.caller.ask(self.state.plan_prompt)
        if "response" in self.state.plan.keys():
            self.state.plan = self.state.plan["response"]
        self.log_prompt(self.state.plan)
        action = {'action':'move', 'building': self.state.plan['building'], 'purpose': self.state.plan['purpose'],'time':self.get_game_time()}
        self.log_actions(action)

    async def use(self, equipment: str, operation: str, description: str, menu: str) -> None:
        # can fail
        # equipment returns usage infomation
        buildings = {"Sheldon":["Sheldon and Leonard's apartment"],
                     "Leonard":["University Physics Department Office"],
                     "Penny":["University Physics Department Office"],
                     "Raj":["Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Howard":["Amy's house","Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Amy":["Sheldon and Leonard's apartment"]}
        self.state.use_prompt = self.prompts.get_text("use", {
            "{name}": self.name,
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{buildings}": buildings[self.name],
            "{plan}": self.state.plan,
            "{act}": self.state.act,
            "{equipment}": equipment,
            "{operation}": operation,
            "{description}": description,
            "{menu}": menu,
            "{act_cache}": self.cache.act_cache,
        })
        self.log_prompt(self.state.use_prompt)
        # {"continue_time": xxx, "result": xxx, "cost": 0, "earn": 0}
        self.state.use =  await self.caller.ask(self.state.use_prompt)
        self.log_prompt(self.state.use)
        if "continue_time" in self.state.use and isinstance(self.state.use["continue_time"], str):
            if re.findall(r"\d+?", self.state.use["continue_time"], re.DOTALL):
                time_string = self.state.use["continue_time"]
                base = 60 * 60 * 1000
                if "minute" in time_string:
                    base = 60 * 1000
                    time_string = time_string.replace("minutes", "").replace("minute", "")
                elif "hour" in time_string:
                    base = 60 * 60 * 1000
                    time_string = time_string.replace("hours", "").replace("hour", "")
                elif "day" in time_string:
                    base = 24 * 60 * 60 * 1000
                    time_string = time_string.replace("days", "").replace("day", "")
                elif "month" in time_string:
                    base = 30 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("months", "").replace("month", "")
                elif "season" in time_string:
                    base = 3 * 30 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("seasons", "").replace("season", "")
                elif "year" in time_string:
                    base = 365 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("years", "").replace("year", "")
                elif "decade" in time_string:
                    base = 10 * 365 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("decades", "").replace("decade", "")
                elif "century" in time_string:
                    base = 100 * 365 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("centuries", "").replace("century", "")
                elif time_string.endswith("s"):
                    time_string = re.findall(r"\d+", time_string, re.DOTALL)[0]
                    if float(time_string) < 1:
                        time_string = "0.5"
                self.state.use["continue_time"] = int(float(time_string) * base)
            else:
                self.state.use["continue_time"] = 30 * 60 * 1000
        if "continue_time" not in self.state.use:
            self.state.use["continue_time"] = 30 * 60 * 1000
        if "result" not in self.state.use:
            self.state.use["result"] = "failed"
        if "bought_thing" not in self.state.use:
            self.state.use["bought_thing"] = ""
        if "amount" not in self.state.use:
            self.state.use["amount"] = 0
        else:
            try:
                self.state.use["amount"] = int(self.state.use["amount"])
            except Exception:
                self.state.use["amount"] = 1
        if "earn" not in self.state.use:
            self.state.use["earn"] = 0
        else:
            try:
                self.state.use["earn"] = int(self.state.use["earn"])
            except Exception:
                self.state.use["earn"] = 200
        self.log_prompt(self.state.use)
        self.cache.act_cache.append({
            "equipment": equipment,
            "operation": operation,
            "continue_time": self.state.use['continue_time'],
            "result": self.state.use['result'],
        })

    async def memory_store(self) -> None:
        # memory cache -> memory data
        # self.experience()
        buildings = {"Sheldon":["Sheldon and Leonard's apartment"],
                     "Leonard":["University Physics Department Office"],
                     "Penny":["University Physics Department Office"],
                     "Raj":["Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Howard":["Amy's house","Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Amy":["Sheldon and Leonard's apartment"]}
        self.state.memory_prompt = self.prompts.get_text("memory_store", {
            "{profile}": self.profile,
            "{memory}": self.memory_data.get_memory(),
            "{buildings}": buildings[self.name],
            "{plan}": self.state.plan,
            "{act_cache}": self.cache.act_cache,
            "{chatCache}": self.cache.chat_cache,
            "{issuccess}": self.state.critic.get("result", "fail"),
        })
        self.log_prompt(self.state.memory_prompt)
        # {
        #    "people": {"John": {"impression": "xxx", "newEpisodicMemory": "xxx"}},
        #    "building": {"School": {"impression": "xxx", "newEpisodicMemory": "xxx"}},
        # }
        self.state.memory = await self.caller.ask(self.state.memory_prompt)
        self.log_prompt(self.state.memory)

    def to_json(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.timestamp(),
            "memory_data": self.memory_data.to_json(),
            "state": self.state.to_json(),
            "cache": self.cache.to_json(),
            "caller": self.caller.model,
            "prompts": self.prompts.to_json(),
            "controller": self.controller.to_json(),
            "name": self.name,
            "bio": self.bio,
            "goal": self.goal,
        }
    
    def from_json(self, obj: Dict[str, Any]):
        self.start_time = datetime.datetime.fromtimestamp(obj.get("start_time", 0))
        self.memory_data.from_json(obj.get("memory_data", dict()))
        self.state.from_json(obj.get("state", dict()))
        self.cache.from_json(obj.get("cache", dict()))
        self.caller = LLMCaller(obj.get("caller", "gpt-4"))
        self.prompts.from_json(obj.get("prompts", dict()))
        self.controller.from_json(obj.get("controller", dict()))
        self.name = obj.get("name", "")
        self.bio = obj.get("bio", "")
        self.goal = obj.get("goal", "")
    
    def cover_prompt(self, prompt_type: str, text: str) -> None:
        self.prompts.prompts[prompt_type].cover(text)

    async def _qa_framework(self) -> None:
        """
        flexible
        """
        # Bio Goal Memory Buildings
        
        buildings = {"Sheldon":["Sheldon and Leonard's apartment"],
                     "Leonard":["University Physics Department Office"],
                     "Penny":["University Physics Department Office"],
                     "Raj":["Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Howard":["Amy's house","Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Amy":["Sheldon and Leonard's apartment"]}
        self.state.question_prompt = self.prompts.get_text("qa_framework_question", {
            "{profile}": self.profile,
            "{memory}": self.memory_data.get_impression_memory(),
            "{buildings}":buildings[self.name],
        })
        self.log_prompt(self.state.question_prompt)
        self.state.question =  await self.caller.ask(self.state.question_prompt)
        self.log_prompt(self.state.question)
        self.state.answer_prompt = self.prompts.get_text("qa_framework_answer", {
            "{profile}": self.profile,
            "{memory}": self.memory_data.get_impression_memory(),
            "{buildings}": buildings[self.name],
            "{question}": self.state.question,
        })
        self.log_prompt(self.state.answer_prompt)
        self.state.answer =  await self.caller.ask(self.state.answer_prompt)
        self.log_prompt(self.state.answer)
    
    async def act(self) -> None:
        memory = {
            "people": {k: {"name": v["name"], "relationShip": v["relationShip"], "impression": v["impression"]} for k, v in self.memory_data.people.items()},
            "building": self.memory_data.get_building_memory(self.state.plan.get("building", "")),
            "experience": self.memory_data.experience,
        }
        # peopleInVision equipmentInVision
        profile = self.profile
        if isinstance(profile,dict):
            if "interpersonal_relationships" in profile.keys():
                del profile["interpersonal_relationships"]
        self.state.act_prompt = self.prompts.get_text("act", {
            "{profile}": profile,
            "{memory}": memory,
            "{equipments}": [f["name"] for f in self.state.equipments],
            "{plan}": self.state.plan,
            "{act_cache}": self.cache.act_cache,
        })
        self.log_prompt(self.state.act_prompt)
        # {"action": "use/chat/experience", "equipment": "ifUse", "operatizon": "ifUse", "person": "ifChat", "topic": "ifChat", "experienceID": "id"}
        act = await self.caller.ask(self.state.act_prompt)
        if isinstance(act,str):
            act = json.loads(act)

        if "response" in act.keys():
            act = act['response']
        self.state.act = act
        if isinstance(self.state.act, dict) and 'action' in self.state.act.keys():
            if self.state.act['action'] == 'use':
                action = {'action':'use','operation':self.state.act['operation'],'time':self.get_game_time()}
                self.log_actions(action)
        self.log_prompt(self.state.act)
    
    def get_profile(self, name):
        profile_path = os.path.join(ROOT_PATH,'profile.json')
        file = open(profile_path, 'r', encoding='utf-8')
        data = json.load(file)
        for item in data:
            if item['name']==name:
                profile = item
                file.close()
                # profile.pop("long_term_goal")
                return profile
        return "none"
            
    def normalize_L2(self, x):
        return x / np.sqrt((x ** 2).sum(-1, keepdims=True))
    
    
    def get_chat_history(self, index_file: str, knowledge_base: str, query_topic: str):
        chat_history = 'None'
        # if query_topic:
        #     index = faiss.read_index(index_file)

        #    
        #     try:
        #       response = requests.post('http://xxx/embedding', json={
        #           'messages': [query_topic],
        #           'embedding_type': 'm3e',
        #           'lm_type': 'lizhi'
        #       }).json()
        #       query_embedding = response['embedding']
        #       query_vec_normalized = self.normalize_L2(np.array(query_embedding).reshape(1,-1).astype('float32'))
        #       k = 1  
        #       D, I = index.search(query_vec_normalized, k)
        #       similarity_score = D[0][0] 
  
        #       if similarity_score>0.85:
        #           file = open(knowledge_base, 'r', encoding='utf-8')
        #           data = json.load(file)
        #           most_similar_data = data[I[0][0]] 
  
        #           if self.name.lower() in most_similar_data['participants'].keys(): 
        #               lines = most_similar_data['lines']
        #               lines = lines if len(lines)<=10 else lines[:10] 
        #               history = []
        #               for i in lines:
        #                   history.append({"speaker":i[0], "content":i[1]})
                      
        #               
        #               f = open(os.path.join(ROOT_PATH,'agent/prompt/determine.txt'),'r',encoding='utf-8')
        #               content = f.read()
        #               determine_prompt = content.format(topic=query_topic, chatHistory=str(history))
        #               f.close()
        #               is_relevant = self.caller.determine_ask(determine_prompt)
        #               if "yes" in is_relevant or "Yes" in is_relevant:
        #                   chat_history = str(history) 
        #               chat_history = str(history)
        #           file.close()
        #     except:
        #       print("Embedding api: http://xxx/embedding doesn't work")
              
            
        return chat_history
    
    def deduplicate_chatcache(self):
        chats = []
        for elem in self.cache.chat_cache:
            if elem not in chats:
                chats.append(elem)
        
        if len(chats)==0:
            return "None"
        else:
            return chats   
    
    
    def get_dialogue_demonstration(self, knowledge_base: str):
        import random
        f = open(knowledge_base, 'r', encoding='utf-8')
        r = json.load(f)
        f.close()
        cnt = len(r)
        found = False
        while not found:
            id = random.randint(0,cnt)
            if self.name.lower() in r[id]['participants'].keys():
                found = True
                dialogue_demonstration = []
                for item in r[id]['lines']:
                    dialogue_demonstration.append(item[1])
        return dialogue_demonstration
    
    def update_ask(self, prompt: str, model="gpt-4o") -> str:
        from openai import OpenAI
        counter = 0
        result = "{}"
        while counter < 3:
            try:
                ### TODO
                client = OpenAI(api_key = '', base_url = '')
                ### TODO

                completion = client.chat.completions.create(
                    model= model,
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
        
    def update(self):
        import ast
        variable_attributes_path = os.path.join(ROOT_PATH,'va.json')
        agent_name = self.name
        conversation_history = self.cache.chat_cache
        profile = self.get_profile(self.name)
        emotion_list = ["neutral", "disgusted", "afraid","sad", "surprised", "happy", "angry"]
        
        emotion_update_prompt = f"In the following conversation, what emotion does {agent_name} express?\n{conversation_history}\nPlease respond only with one word from this list [\"neutral\", \"disgusted\", \"afraid\",\"sad\", \"surprised\", \"happy\", \"angry\"]."
        
        # short_term_goal_update_prompt = f"Please set new short-term goal based on {agent_name}'s long-term goal, the conversations that have occurred now, and previous short-term goal.\n\n{agent_name}'s long-term goal: {profile['long_term_goal']}\nThe conversations that have occurred now: {conversation_history}\n{agent_name}'s previous short-term goal: {profile['short_term_goal']}\n\n"+"Your new short-term goal should be different from the previous short-term goal. Here is an example of what you need to return in json format:\n{'new short-term goal':xxx}. \nYou should just tell the sentences you want to speak in the above JSON format."
        
        personality_update_prompt = f"Please make slight changes to the original personality of {agent_name} based on the dialogue provided. It is required that the changed personality be almost the same as the original personality in sentence structure, except for some changes in some vocabulary describing the personality.\n\n**The following is the dialogue {agent_name} participated in**: \n{conversation_history}\n**This is {agent_name}'s original personality**: {profile['personality']}\n\n"+"Please only return the changed personality:\n"
        
        emotion_status = self.update_ask(emotion_update_prompt)
        self.log_prompt(emotion_update_prompt)
        self.log_prompt(emotion_status)
        print("\n\n\n")
        print(emotion_update_prompt)
        print(emotion_status)
        print("\n\n\n")
        # short_term_goal = self.update_ask(short_term_goal_update_prompt, model="gpt-3.5-turbo-1106")
        personality = self.update_ask(personality_update_prompt)
        
        file = open(variable_attributes_path, 'r', encoding='utf-8')
        va = json.load(file)
        file.close()
        if emotion_status in emotion_list:
            va[agent_name]['emotion_status'] = emotion_status
        
        va[agent_name]['personality'] = personality
        # try:
        #     content = ast.literal_eval(personality)
        #     personality = content['personality']
        #     va[agent_name]['personality'] = personality
        # except:
        #     print("There are some errors when use ast module.")

        file = open(variable_attributes_path, 'w', encoding='utf-8')
        json.dump(va, file, ensure_ascii=False)
        file.close()
        
        
        
    async def chat(self, person: str, topic: str, npc="") -> None:
        #if npc:
        
        #    profile = self.get_profile(npc)
        #else:
        #    profile = self.profile 
        profile = self.get_profile(self.name)   
        chats = self.deduplicate_chatcache()
        knowledge_base = os.path.join(ROOT_PATH,'The_big_bang_theory.json')
        faiss_path = os.path.join(ROOT_PATH,'index.faiss')
        dialogue_demonstration = self.get_dialogue_demonstration(knowledge_base)
        file = open(os.path.join(ROOT_PATH,'va.json'), 'r', encoding='utf-8')
        va = json.load(file)
        file.close()
        
        self.state.chat_prompt = self.prompts.get_text("chat", {
            "{mood}": va[self.name]['emotion_status'],
            "{name}": profile["name"],
            "{gender}": profile["gender"],
            "{occupation}": profile["occupation"],
            "{personality}": profile["personality"],
            "{interpersonal_relationships}": profile["interpersonal_relationships"],
            "{short_term_goal}": profile["short_term_goal"],
            # "{memory}": self.memory_data.get_people_memory(person),
            # "{buildings}": self.state.buildings,
            # "{plan}": self.state.plan,
            # "{act}": self.state.act,
            "{chatTo}": person,
            "{chatTopic}": topic,
            "{chatHistory}": self.get_chat_history(faiss_path,knowledge_base,topic),
            "{chats}": self.cache.chat_cache,
            "{dialogue_demonstration}": dialogue_demonstration
        })
        # {"context": "xxx"}
        self.log_prompt(self.state.chat_prompt)
        self.state.chat = await self.caller.ask(self.state.chat_prompt)
        if "response" in self.state.chat.keys():
            self.state.chat = self.state.chat['response']
        if isinstance(self.state.chat, str):
            self.state.chat = json.loads(self.state.chat)
        self.log_prompt(self.state.chat)
        action = {'action':'chat', 'speaker':self.name, 'person':person, 'topic':topic, 'chats':self.cache.chat_cache, 'reply':self.state.chat,'time':self.get_game_time()}
        self.log_actions(action)
        self.chat_cnt=self.chat_cnt+1
        if self.chat_cnt%5==0:
            print("&&&&&&&&&&&&&&&&&&&&&&&&&&------------------------------------------")
            self.update()
            
            
        
        
    
    async def critic(self) -> None:
        # _use: usage infomation plan
        # decides whether plan finished
        buildings = {"Sheldon":["Sheldon and Leonard's apartment"],
                     "Leonard":["University Physics Department Office"],
                     "Penny":["University Physics Department Office"],
                     "Raj":["Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Howard":["Amy's house","Raj's house","Howard's house", "restaurant","Comic book store"],
                     "Amy":["Sheldon and Leonard's apartment"]}
        memory = self.memory_data.get_impression_memory()
        memory["experience"] = self.memory_data.experience
        self.state.critic_prompt = self.prompts.get_text("critic", {
            "{profile}": self.profile,
            "{memory}": memory,
            "{buildings}": buildings[self.name],
            "{plan}": self.state.plan,
            "{act}": self.state.act,
            "{use}": self.state.use,
            "{act_cache}": self.cache.act_cache,
        })
        self.log_prompt(self.state.critic_prompt)
        # {"result": "success", "fitScore": 0-10}
        # {"result": "fail", "needToDo": "xxx"}
        # {"result": "not_finished_yet"}
        self.state.critic = await self.caller.ask(self.state.critic_prompt)
        self.log_prompt(self.state.critic)
    
    def experience(self) -> None:
        # packing act caches & plan to experience
        # self.cache.experienceCache.append({"plan": self.state.plan, "acts": self.cache.act_cache})
        if self.cache.act_cache:
            print(self.cache.act_cache)
            eid = str(len(self.memory_data.experience) + 1)
            self.memory_data.experience[eid] = {"experienceID": eid, "plan": self.state.plan, "acts": self.cache.act_cache.copy()}
            print(self.memory_data.experience[eid])
            self.cache.act_cache = list()
            print(self.cache.act_cache)
            # self.cache.plan_cache.append({"time": self.get_game_time(), "plan": self.state.plan})
    
    def get_game_time(self):
        game_time = self.state.game_time - self.start_time
        return f"day {game_time.days} {self.state.game_time.strftime('%H:%M')}"
    