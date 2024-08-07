import tornado.ioloop
# import tornado.web
import tornado.websocket
# import subprocess
import re
import os
import json
from openai import OpenAI
import ast

from app import App

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

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    app_cache = App()
    ping_interval = 0

    def check_origin(self, remote_address):
        # CORS
        return True

    def open(self):
        self.app_cache.register(self)

    def on_close(self):
        # print("connection closing")
        self.app_cache.logout(self)

    async def on_message(self, message):
        await self.app_cache.execute(self, message)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/ws', WebSocketHandler),
        ]
        tornado.web.Application.__init__(self, handlers, websocket_ping_interval=0)

### TODO
ROOT = ""
### TODO

def set_simualtion():

    
    predix = "There are six characters: Sheldon, Leonard, Howard, Raj, Amy, Penny.\nHere is the synopses of their previous stories: {}\n\n"
    postdix = "According to the synopses, you need to brainstorm the next multi-line story(at least 200 words) and determine a short term goal(what she or he plans to do next) for each character in Sheldon, Leonard, Howard, Raj, Amy, Penny based on your story. The story should include Sheldon asking Leonard and Penny for help because Amy rejected his proposal and broke up with him.\n\nHere is an example of what you need to return in json format:\n{'story':xxx, 'short term goal':{'Sheldon':xxx, 'Leonard':xxx, ...}}. \nYou should just tell the sentences you want to speak in the above JSON format."
    


    story_path = os.path.join(ROOT, "The_big_bang_story.json")
    profile_path = os.path.join(ROOT, "profile.json")
    
    f = open(story_path, 'r')
    storys = json.load(f)
    # pre_story = storys[-4]['text'] + '\n' + storys[-3]['text'] + '\n' + storys[-2]['text'] + '\n' + storys[-1]['text']
    pre_story = storys[-1]['text']
    f.close()
    prompt = predix.format(pre_story) + postdix
    counter = 0
    print(prompt)
    while counter < 3:
        try:
            ### TODO
            client = OpenAI(api_key = '', base_url = '')
            ### TODO

            completion = client.chat.completions.create(
                # model="gpt-4-turbo-preview", 
                model = "gpt-4o",
                messages=[
                    {"role": "user", "content": prompt},
                ]
            )

            result = completion.choices[0].message.content
            result = clean_text(result)
            print(result)
            content = ast.literal_eval(result)
            short_term_goals = content['short term goal']
            print("Based on the previous plot, I brainstormed the following plot:\n", content['story'])
            print("Short-term goals for each role:\n", short_term_goals)
            
            # Added new plot to the knowledge base
            f = open(story_path, 'w')
            storys.append({'text':content['story']})
            json.dump(storys, f, ensure_ascii=False)
            f.close()
            
            # Modify the goal of each role in the profile file
            f = open(profile_path, 'r')
            r = json.load(f)
            data = []
            for item in r:
                name = item['name']
                item['short_term_goal'] = short_term_goals[name]
                data.append(item)

                
            f.close()
            
            w = open(profile_path, 'w')
            json.dump(data, w, ensure_ascii=False)
            w.close()
            break

        except Exception as e:
            print(e)
            counter += 1


def ini_va():
    va = {
        "Sheldon": {
            "emotion_status": "neutral",
            "personality": "Sheldon is a smart but eccentric character with poor social skills, a sharp tongue, tendencies towards obsessive-compulsive behavior, apparent narcissistic traits, and often appears rude and conceited."
        },
        "Leonard": {
            "emotion_status": "neutral",
            "personality": "Leonard is a geeky yet sociable character with a friendly demeanor, who occasionally shows a mean streak and struggles with jealousy and insecurity, especially regarding his interactions with Penny and other men."
        },
        "Penny": {
            "emotion_status": "neutral",
            "personality": "Penny is a kind-hearted and empathetic character with great social skills, despite being somewhat dim-witted, but she deeply loves Leonard and their friends even when displaying a bad attitude or selfish acts."
        },
        "Howard": {
            "emotion_status": "neutral",
            "personality": "Howard is a cheeky, tenderhearted, and self-proclaimed suave character, who can also be obnoxious and arrogantly derisive, yet remains extremely sensitive to criticism from women."
        },
        "Raj": {
            "emotion_status": "neutral",
            "personality": "Raj is a childlike, selectively mute character who is kind and humorous among friends, yet occasionally revels in others' misfortunes for personal gain."
        },
        "Amy": {
            "emotion_status": "neutral",
            "personality": "Amy is a narcissistic, blunt, and nerdy character with a unique sense of humor and unusual hobbies, often making others feel awkward."
        }
    }
    
    f = open(os.path.join(ROOT, "va.json"), 'w')
    json.dump(va, f, ensure_ascii=False)
    f.close()



if __name__ == "__main__":
    print("----------Server Started----------")
    app = Application()
    app.listen(8000, address='0.0.0.0')
    ini_va()
    # set_simualtion()
    # subprocess.call("python3 -u tick.py")
    tornado.ioloop.IOLoop.current().start()
    print("----------Server Stopped----------")
