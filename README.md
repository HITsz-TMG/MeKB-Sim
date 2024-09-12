# MeKB-Sim: Personal Knowledge Base-Powered Multi-Agent Simulation 🌐


[![Paper](https://img.shields.io/badge/Paper-MeKB_Sim-yellow)](https://mekb-sim.github.io/static/MeKB_Sim_Paper.pdf)
[![Game Interface](https://img.shields.io/badge/Demo-Game_Interface-blue)](http://49.51.252.71:7042/)
[![Monitoring Panel](https://img.shields.io/badge/Demo-Monitoring_Panel-orange)](http://49.51.252.71:7041/)
[![Video](https://img.shields.io/badge/Video-Youtube-red)](https://youtu.be/5yWK6QcAyxc)


🚀 We are excited to introduce **MeKB-Sim**, a multi-agent simulation platform that closely mimic real-life interactions, based on a dynamic personal knowledge base, termed **MeKB**.

🤖 The MeKB of each agent consists of attributes crucial for modeling theory of mind, such as linguistic style, personality, and memory.
The dynamic nature of MeKB to enable agents to adapt their activities and interactions with other agents effectively. 



Our platform includes a Unity WebGL game interface
for visualization and an interactive monitoring panel that presents the agents’ planning,
actions, and MeKBs over time. 
**Dive into our simulation 🕹️ – click the image below for a YouTube video walkthrough!**


[![MeKB-Sim demo front end](https://github.com/HITsz-TMG/MeKB-Sim/blob/main/front_end.png)](https://www.youtube.com/watch?v=_-5bbsgywFc)


## 🌟 Environment

### Dependency
```
python: 3.9.18
mysql: 8.0.31
node.js: 18.19.1
```

### Folder Creation
```
mkdir logs
mkdir actions
mkdir snapshot
```

### Mysql Init
```
create database `llm_account` default character set utf8mb4 collate utf8mb4_unicode_ci;
create database `llm_game` default character set utf8mb4 collate utf8mb4_unicode_ci;
create database `llm_game0001` default character set utf8mb4 collate utf8mb4_unicode_ci;
create database `llm_game0002` default character set utf8mb4 collate utf8mb4_unicode_ci;
```
In order to connect to mysql, you need to modify `config/app.json.`

### Install
```
pip install -r requirements.txt
```

## ⚡️ How to deploy your demo

### Code Modification
You need to modify the contents marked with ***"### TODO"*** in the following files
```
agent/agent/agent.py
agent/utils/llmExpends/gpt4.py
agent/utils/llmExpends/gpt35.py
main.py
show_actions.py
```

Besides, modify the contents marked with ***"// TODO"*** in `client/Build/Builds.framework.js`

### Run
#### 1. To start the demo backend, run
```
python main.py
```
When you see
```
--------Server Started--------
```
The backend has been started successfully.

#### 2. To start the unity webgl client, open `client/index.html` in your browser.
a. Right-clicking the index.html in your python IDE and select open in browser.  

b. Or in directory ***client***, run
```
python -m http.server 7042 --bind 0.0.0.0
```
Then visit the following address in your browser
```
http://127.0.0.1:7042
```
When you see
```
somebody linked.
```
The client has been started successfully.

#### 3. To start the backend of the monitoring page, run
```
python show_actions.py
```

#### 4. To start the Vue front-end of the monitoring page
Create a new vue project and replace the corresponding files in the new vue project with the two files under `monitor_page-vue/src`. 

Then modify the ***backendServer*** in the `main.js`

#### 5. Start Simulation
You can start ***tick*** with the buttons on the web client. You can also start with:
```
python tick.py
```

#### 6. Restart
```
rm -f snapshot/app.json
rm -f actions/*
```
```
drop database llm_account;
drop database llm_game0001;
create database `llm_game0001` default character set utf8mb4 collate utf8mb4_unicode_ci;
create database `llm_account` default character set utf8mb4 collate utf8mb4_unicode_ci;
```
Then re-run
```
python main.py
```

## 🌈 Citation
If you find MeKB-Sim useful for your research and applications, please cite using this BibTeX:
```

```
