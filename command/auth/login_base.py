from command.command_base import CommandBase
from agent.actor import Actor


class LoginBase(CommandBase):

    def reg_npc(self, uid, nickname, x, y, asset, bio, goal, home_building=3,work_building=0):
        account_model = self.get_model('NPCRegister')
        # print(f'!!! when register npc uid: {uid}-{nickname}')
        print(f'!!! when register database: {account_model.get_db()}')
        id = account_model.find_id(f'{uid}-{nickname}')
        if id <= 0:
            id = account_model.reg_npc(f'{uid}-{nickname}')
            if id <= 0:
                return self.error('register npc failed')
        npc_uid = self.gen_token("NPC", id)
        npc_model = self.get_single_model("NPC", id=id, create=True)
        npc_model.name = nickname
        npc_model.map = self.id
        # TODO: If agent use websocket connect with server
        # Then don't set server and use this field to search npcs not linked
        npc_model.server = npc_uid
        npc_model.cash = 10000
        npc_model.x = x
        npc_model.y = y
        npc_model.rotation = 0
        npc_model.asset = asset
        npc_model.save()
        
        # buildings_model = self.get_single_model("Buildings", create=False)
        buildings = ["Sheldon and Leonard's apartment", "Penny's apartment", "Comic book store", "University Physics Department Office", "Amy's house","Raj's house","Howard's house", "restaurant"]
        model = "gpt-4"
        memorySystem = "LongShortTermMemories"
        planSystem = "QAFramework"
        npc_model.model = model
        npc_model.memorySystem = memorySystem
        npc_model.planSystem = planSystem
        npc_model.bio = bio
        npc_model.goal = goal
        npc_model.home_building = home_building
        npc_model.work_building = work_building
        # if buildings_model:
        #     buildings = buildings_model.get_names()
        self.app.actors[npc_uid] = Actor(nickname, bio, goal, model, memorySystem, planSystem, buildings, 10000, self.app.last_game_time)
        self.app.inited.add(npc_uid)
        return id, npc_model

    def reg_eval(self, uid):
        for eval_des, eval_cfg in self.app.eval_configs.items():
            eval_model = self.get_single_model('Eval', id=uid, create=True, eval_cfg=eval_cfg)
            self.app.evals[eval_des] = eval_model
        return eval_model


    # Common login logic.
    def handle_login(self, nickname, uid):
        buildings_info = []
        npcs_info = []
        player_model = self.get_single_model('Player', create=False)
        npc_configs = self.app.get_npc_config()
        # First time login, create all data to avoid creating them in scene server.
        # Otherwise, to update login time.
        if player_model is None:
            print(uid, "first login")
            Penny, Penny_model = self.reg_npc(uid, "Penny", 52, 7, "premade_02", "An aspiring actress and waitress, she lives passionately and focuses on immediate pleasure.", "To find a more stable career path and establish enduring romantic relationships.",4)
            Leonard, Leonard_model = self.reg_npc(uid, "Leonard", 84, 27, "premade_03", "A physicist, Sheldon's roommate, more socially adept but often troubled by Sheldon's eccentricities", "To aim for success in physics and desires fulfillment in romantic relationships, particularly with Penny.",2)
            Howard, Howard_model = self.reg_npc(uid, "Howard", 50, 45, "premade_05", "A mechanical engineer who considers himself a ladies' man, often seen in tight pants and retro-style clothes.", "To be perceived as successful and charismatic, often manifested in his pursuit of women. As an engineer, he also aims for professional achievements.",5)
            Raj, Raj_model = self.reg_npc(uid, "Raj", 113, 45, "premade_07", "An astrophysicist from India who initially couldn't speak in front of women.", "To overcome his shyness in communicating with women and to gain recognition in his professional field.",3)
            Amy, Amy_model = self.reg_npc(uid, "Amy", 112, 11, "premade_04", "A neurobiologist, becomes Sheldon's girlfriend, sharing some of his social challenges.", "To achieve success in science and develop her relationship with Sheldon. ",6)
            Sheldon, Sheldon_model = self.reg_npc(uid, "Sheldon", 82, 25, "premade_01", "A highly intelligent theoretical physicist with quirky behavior and a lack of social skills, passionate about science and comics.", "To achieve excellence in theoretical physics and learn how to better interact and form relationships with others.",2)
            
            models = [
                'Player',
                'Map',
                'Town',
                'Buildings',
                'Equipments',
                'NPCs',
            ]
            for model_name in models:
                model = self.get_single_model(model_name)
                # if model_name == "NPCs":
                    # last_npcs = model.npcs
                    # for nid in last_npcs:
                    #     nuid = self.gen_token("NPC", nid)
                    #     if nuid in self.app.movings:
                    #         self.app.movings.remove(nuid)
                    #     if nuid in self.app.chatted:
                    #         self.app.chatted.remove(nuid)
                    #     if nuid in self.app.using:
                    #         self.app.using.remove(nuid)
                    #     if nuid in self.app.inited:
                    #         self.app.inited.remove(nuid)
                    #     self.app.cache = [c for c in self.app.cache if c["uid"] != nuid]
                    #     if nuid in self.app.actors:
                    #         del self.app.actors[nuid]
                model.init()
                if model_name == "Player":
                    model.name = nickname
                    model.x = 100
                    model.y = 41
                if model_name == "Map":
                    model.init_map()
                    model.add_uid(100, 41, uid, nickname)
                    model.add_uid(82, 25, f"NPC-{Sheldon}", "Sheldon")
                    model.add_uid(84, 27, f"NPC-{Leonard}", "Leonard")
                    model.add_uid(50, 45, f"NPC-{Howard}", "Howard")
                    model.add_uid(113, 45, f"NPC-{Raj}", "Raj")
                    model.add_uid(112, 11, f"NPC-{Amy}", "Amy")
                    model.add_uid(52, 7, f"NPC-{Penny}", "Penny")
                if model_name == "Buildings":
                    model.init_buildings()
                    for building in model.buildings:
                        # if building["lC"] > 0:
                        if building["n"]=="Sheldon and Leonard's house":
                            model.add_tenent(building["id"], Sheldon)
                            model.add_tenent(building["id"], Leonard)
                        if building["n"]=="Penny's house":
                            model.add_tenent(building["id"], Penny)
                        if building["n"]=="Howard's house":
                            model.add_tenent(building["id"], Howard)
                        if building["n"]=="Raj's house":
                            model.add_tenent(building["id"], Raj)
                        if building["n"]=="Amy's house":
                            model.add_tenent(building["id"], Amy)
                        buildings_info.append({"building_id": building["id"], "building_type": building["t"], "name": building["n"], "x": building["x"], "y": building["y"]})
                if model_name == "Equipments":
                    model.init_equipments()
                if model_name == "NPCs":
                    model.npcs = [{"id": Sheldon, "name": "Sheldon"}, {"id": Leonard, "name": "Leonard"}, {"id": Penny, "name": "Penny"}, {"id": Amy, "name": "Amy"}, {"id": Raj, "name": "Raj"}, {"id": Howard, "name": "Howard"}]
                    # for npc in model.npcs:
                    #     npc_model = self.get_single_model("NPC", npc["id"], create=False)
                    #     if not npc_model:
                    #         continue
                    #     home_building = self.get_single_model("Buildings", create=True).get_building(npc_model.home_building)
                    #     if not home_building:
                    #         continue
                    npcs_info.append({"uid": f"NPC-{Sheldon}", "homeBuilding": Sheldon_model.home_building, 'asset': npc_configs.assets.index(Sheldon_model.asset), "assetName": Sheldon_model.asset, 'model': Sheldon_model.model, 'memorySystem': Sheldon_model.memorySystem, 'planSystem': Sheldon_model.planSystem, 'workBuilding': Sheldon_model.work_building, 'nickname': Sheldon_model.name, 'bio': Sheldon_model.bio, 'goal': Sheldon_model.goal, 'cash': Sheldon_model.cash, "x": Sheldon_model.x, "y": Sheldon_model.y})

                    npcs_info.append({"uid": f"NPC-{Leonard}", "homeBuilding": Leonard_model.home_building, 'asset': npc_configs.assets.index(Leonard_model.asset), "assetName": Leonard_model.asset, 'model': Leonard_model.model, 'memorySystem': Leonard_model.memorySystem, 'planSystem': Leonard_model.planSystem, 'workBuilding': Leonard_model.work_building, 'nickname': Leonard_model.name, 'bio': Leonard_model.bio, 'goal': Leonard_model.goal, 'cash': Leonard_model.cash, "x": Leonard_model.x, "y": Leonard_model.y})

                    npcs_info.append({"uid": f"NPC-{Penny}", "homeBuilding": Penny_model.home_building, 'asset': npc_configs.assets.index(Penny_model.asset), "assetName": Penny_model.asset, 'model': Penny_model.model, 'memorySystem': Penny_model.memorySystem, 'planSystem': Penny_model.planSystem, 'workBuilding': Penny_model.work_building, 'nickname': Penny_model.name, 'bio': Penny_model.bio, 'goal': Penny_model.goal, 'cash': Penny_model.cash, "x": Penny_model.x, "y": Penny_model.y})

                    npcs_info.append({"uid": f"NPC-{Howard}", "homeBuilding": Howard_model.home_building, 'asset': npc_configs.assets.index(Howard_model.asset), "assetName": Howard_model.asset, 'model': Howard_model.model, 'memorySystem': Howard_model.memorySystem, 'planSystem': Howard_model.planSystem, 'workBuilding': Howard_model.work_building, 'nickname': Howard_model.name, 'bio': Howard_model.bio, 'goal': Howard_model.goal, 'cash': Howard_model.cash, "x": Howard_model.x, "y": Howard_model.y})

                    npcs_info.append({"uid": f"NPC-{Raj}", "homeBuilding": Raj_model.home_building, 'asset': npc_configs.assets.index(Raj_model.asset), "assetName": Raj_model.asset, 'model': Raj_model.model, 'memorySystem': Raj_model.memorySystem, 'planSystem': Raj_model.planSystem, 'workBuilding': Raj_model.work_building, 'nickname': Raj_model.name, 'bio': Raj_model.bio, 'goal': Raj_model.goal, 'cash': Raj_model.cash, "x": Raj_model.x, "y": Raj_model.y})

                    npcs_info.append({"uid": f"NPC-{Amy}", "homeBuilding": Amy_model.home_building, 'asset': npc_configs.assets.index(Amy_model.asset), "assetName": Amy_model.asset, 'model': Amy_model.model, 'memorySystem': Amy_model.memorySystem, 'planSystem': Amy_model.planSystem, 'workBuilding': Amy_model.work_building, 'nickname': Amy_model.name, 'bio': Amy_model.bio, 'goal': Amy_model.goal, 'cash': Amy_model.cash, "x": Amy_model.x, "y": Amy_model.y})
                model.save()
        else:
            print(uid, "login")
            player_model.login_time = self.get_nowtime()
            player_model.save()
            
            buildings_model = self.get_single_model("Buildings", create=False)
            if buildings_model:
                for building in buildings_model.buildings:
                    buildings_info.append({"building_id": building["id"], "building_type": building["t"], "name": building["n"], "x": building["x"], "y": building["y"]})
                    
            npcs_model = self.get_single_model("NPCs", create=False)
            if npcs_model:
                for npc in npcs_model.npcs:
                    npc_model = self.get_single_model("NPC", npc["id"], create=False)
                    if not npc_model:
                        continue
                    npcs_info.append({"uid": f'NPC-{npc["id"]}', "homeBuilding": npc_model.home_building, 'asset': npc_configs.assets.index(npc_model.asset), "assetName": npc_model.asset, 'model': npc_model.model, 'memorySystem': npc_model.memorySystem, 'planSystem': npc_model.planSystem, 'workBuilding': npc_model.work_building, 'nickname': npc_model.name, 'bio': npc_model.bio, 'goal': npc_model.goal, 'cash': npc_model.cash, "x": npc_model.x, "y": npc_model.y})

        # self.reg_eval(uid)
        return buildings_info, npcs_info

    def is_check_token(self):
        return False
