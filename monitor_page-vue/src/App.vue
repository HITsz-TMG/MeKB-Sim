<template>
  <div class="main" style="max-height:100vh; overflow:auto; width:100%">
    <div class="title" style="width:100%; text-align:center"><h2>MeKB-Sim: Personal Knowledge Base-Powered Multi-Agent Simulation</h2></div>
    <el-divider></el-divider>
    <div class="next_story" style="width:100%;">
        <div class="main" style="width:60%; margin-left:20%; box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04); border-radius:8px; padding:10px;">
            <div class="title" style="font-size:20px; margin-bottom:8px">Brainstorm the Next Plot</div>
            <div clas="story" style="padding:8px; border-radius:4px; border:1px #DCDFE6 solid; min-height:120px; max-height:120px; overflow:auto; font-size:16px">{{next_story}}</div>
        </div>
    </div>
    <div class="actions" style="width:100%">
        <div class="actions" style="width:61%; margin-left:20%; margin-top:20px;">
            <div class="activity" style="width:45%; float:left; margin-right:5%">
                <el-tabs v-model="activity_activeName" type="border-card" style="border-radius:8px">
                  <el-tab-pane :label="item.name" :name="item.name" :key="item.id" v-for="item in characters ">
                      <div class="little-title" style="font-size:20px;">All activities</div>
                      <el-divider></el-divider>
                      <div class="activity-list" style="overflow:auto; min-height:400px; max-height:400px">
                          <el-timeline>
                            <el-timeline-item placement="top" v-for="(ite, index) in actions[item.name]" :key="index" :timestamp="ite.time" style="margin-left:-20px">
                              <el-card>
                                <p>{{ite.description}}</p>
                                <el-link type="primary" @click="get_fullchats(ite.contents)" v-if="ite.action=='chat'">Full conversations >></el-link>
                                <p></p>
                                
                                <el-tooltip content="Removed from long-term memory" placement="top" effect="light" v-if="ite.action=='chat'&&ite.button_hidden==false">
                                  <el-button class="remove-button"  icon="el-icon-folder-remove" circle @click="removeMemory(item.name, index)" type="primary" plain style="float:right;margin-bottom:8px"></el-button>
                                </el-tooltip>
                                <el-tooltip content="Added to long-term memory" placement="top" effect="light" v-if="ite.action=='chat'&&ite.button_hidden==true">
                                  <el-button class="remove-button"  icon="el-icon-folder-remove" circle @click="addMemory(item.name, index)" type="info" plain style="float:right;margin-bottom:8px"></el-button>
                                </el-tooltip>
                              </el-card>
                            </el-timeline-item>
                          </el-timeline>
                      </div>
                  </el-tab-pane>  
                </el-tabs> 
            </div>

            <div class="chats" style="width:50%; float:left;">
                <el-tabs type="border-card" style="border-radius:8px">
                    <el-tab-pane>
                        <span slot="label"><i class="el-icon-chat-dot-round"></i> Full conversations</span>
                        <div class="chats-main" style="border:1px #DCDFE6 solid; border-radius:4px; min-height:475px; max-height:475px; overflow:auto">
                            <el-timeline style="margin-left:-50px; width:98%; margin-top:16px">
                              <el-timeline-item v-for="(item, index) in show_full_chats" :key="index" >
                                <el-card>
                                  <h4>{{item.speaker}}</h4>
                                  <p>{{item.content}}</p>
                                </el-card>
                              </el-timeline-item>
                            </el-timeline>  
                        </div>
                    </el-tab-pane>
                </el-tabs>
            </div>
        </div>
    </div>
    <div class="button" style="width:61%; margin-left:20%;">
        <el-button @click="get_actions()" style="width:45%; margin-top:15px; box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04);">Refresh Data</el-button>
        <el-button style="width:50%; margin-left:5%; margin-top:15px; box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04);">Stop Simulation</el-button>
    </div>
    <div class="profile" style="width:60%; margin-left: 20%; text-align: center; box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04); margin-top:20px; padding:10px">
        <div class="title" style="font-size: 20px; margin-bottom:8px">Character Panel</div>
        <div class="profile-main" style="border: 1px #DCDFE6 solid; padding:8px;"> 
            <el-tabs v-model="profile_activeName">
              <el-tab-pane :label="item.name" :name="item.name" :key="item.id" v-for="item in characters ">
                  <div class="profile-info" style="border: 1px #E6A23C solid;">
                    <el-tag type="warning" style="margin-bottom: 10px;">Fixed Attributes</el-tag>
                      <el-descriptions :column="1" border>
                        <el-descriptions-item label="Name">{{ item.name }}</el-descriptions-item>
                        <el-descriptions-item label="Gender">{{ item.gender }}</el-descriptions-item>
                        <el-descriptions-item label="Race">{{ item.race }}</el-descriptions-item>
                        <el-descriptions-item label="Occupation">{{ item.occupation }}</el-descriptions-item>
                        <el-descriptions-item label="Education Level">{{ item.education_level }}</el-descriptions-item>
                        <el-descriptions-item label="Linguistic Style">{{ item.linguistic_style }}</el-descriptions-item>
                        
                        <el-descriptions-item label="Interpersonal Relationships">
                          <el-tag size="small" v-for="(res, index) in item.interpersonal_relationships" :key="index" style="margin-left: 8px; margin-top: 8px">{{res}}</el-tag>
                        </el-descriptions-item>
                        <el-descriptions-item label="Long Term Goal">{{ item.long_term_goal }}</el-descriptions-item>
                      </el-descriptions>
                  </div>
                  <div class="profile-info" style="border: 1px #67C23A solid;margin-top: 20px">
                    <el-tag type="success" style="margin-bottom: 10px;">Variable Attributes</el-tag>
                      <el-descriptions :column="1" border>
                        <el-descriptions-item label="Personality">{{ item.personality }}</el-descriptions-item>
                        <el-descriptions-item label="Short Term Goal">{{ item.short_term_goal }}</el-descriptions-item>
                        <el-descriptions-item label="Emotion Status">{{ item.emotion_status }}</el-descriptions-item>
                      </el-descriptions>
                    <div class="long_memory" style="margin-top: 10px; border:1px #DCDFE6 solid">
                        <div class="title" style="font-size:20px; width:100%; text-align:center;margin-bottom:8px">Long Term Memory</div>
                        <div class="memory" style="width:100%">
                            <el-table :data="tableData[item.name]" stripe style="width: 98%; min-height:420px; max-height:420px; overflow-y:auto">
                              <el-table-column prop="time" label="Time"></el-table-column>
                              <el-table-column prop="memory" label="Event"></el-table-column>
                            </el-table>
                        </div>
                        <el-pagination :page-size="size" layout="prev, pager, next" :total="totalPage[item.name]" @current-change="(val) => handleCurrentChange(item.name, val)" :current-page="currentPage[item.name]"></el-pagination> 
                    </div>
                  </div>
              </el-tab-pane>  
            </el-tabs> 
        </div>
    </div>
  </div>
    
</template>

<script >

export default {
name: 'App',
data() {
  return {
    next_story:'',
    activity_activeName:'Sheldon',
    profile_activeName:'Sheldon',
    characters:[
      {"name": "Sheldon", "id": 0},{"name": "Leonard", "id": 1},{"name": "Penny", "id": 2},
      {"name": "Howard", "id": 3},{"name": "Raj", "id": 4},{"name": "Amy", "id": 5}
    ],
    actions:{
      "Sheldon":[],
      "Leonard":[],
      "Penny":[],
      "Howard":[],
      "Raj":[],
      "Amy":[]
    },
    tableData:{
      "Sheldon":[],
      "Leonard":[],
      "Penny":[],
      "Howard":[],
      "Raj":[],
      "Amy":[]
    },
    currentPage:{
      "Sheldon":1,
      "Leonard":1,
      "Penny":1,
      "Howard":1,
      "Raj":1,
      "Amy":1
    },
    totalPage:{
      "Sheldon":1,
      "Leonard":1,
      "Penny":1,
      "Howard":1,
      "Raj":1,
      "Amy":1
    },
    show_full_chats:[],
    size:5,
    cnt:0
  }
},

mounted(){
  this.get_initdata()
},


methods:{
    //获得故事梗概以及角色的个人数据 
    get_initdata(){
      fetch(this.$root.backendServer+'/get_initdata', {
          method: "post",
          mode: 'cors',
          body: JSON.stringify({
            'stream':false
          }),
          headers: {
              "Content-Type": "application/json"
          }
      }).then(res=>res.json()).then(res=>{
        var all_data = res.response
        this.next_story = all_data['next_story']
        for(var i=0;i<6;i++){
          var item = all_data[this.characters[i]["name"]]
          item["id"] = i
          this.characters[i] = item
        }
        this.changeCurrentChange()
      })  
    },

    //获得完整对话内容
    get_fullchats(data){
      this.show_full_chats = data
    },

    //刷新角色的actions
    get_actions(){
      fetch(this.$root.backendServer+'/get_actions', {
          method: "post",
          mode: 'cors',
          body: JSON.stringify({
            'stream':false
          }),
          headers: {
              "Content-Type": "application/json"
          }
      }).then(res=>res.json()).then(res=>{
        var all_data = res.response
        for(let name in this.actions){
          //this.actions[name].reverse()
          var src_len = this.actions[name].length
          var new_len = all_data[name].length  
          var add_memory = []
          var new_plan = ''
          this.actions[name] = all_data[name]
          for(var i=src_len;i<new_len;i++){
            //this.actions[name].push(all_data[name][i])
            this.actions[name][i]['button_hidden'] = false
            if(this.actions[name][i].action=='chat'){
              add_memory.push({'time':this.actions[name][i].time, 'memory':this.actions[name][i].description})
            }
            if(this.actions[name][i].action=='move'){
              new_plan = this.actions[name][i].description
            }
          }
          for(var j=0;j<6;j++){
            if(this.characters[j].name==name){
              add_memory.reverse()
              this.characters[j].long_memory = add_memory.concat(this.characters[j].long_memory)
              this.changeCurrentChange()
              if (new_plan!=''){
                this.characters[j].short_term_goal = new_plan
              }
              break
            }
          }
          this.actions[name].reverse()
          
        }
      })  

      fetch(this.$root.backendServer+'/get_va', {
          method: "post",
          mode: 'cors',
          body: JSON.stringify({
            'stream':false
          }),
          headers: {
              "Content-Type": "application/json"
          }
      }).then(res=>res.json()).then(res=>{
        var va = res.response
        for(var j=0;j<6;j++){
          this.characters[j].emotion_status = va[this.characters[j].name].emotion_status
          this.characters[j].personality = va[this.characters[j].name].personality
        }
      })  
    },

    //改变分页页面时触发
    changeCurrentChange(){
      for(var i=0;i<6;i++){
          var name = this.characters[i]["name"]
          this.tableData[name] = this.characters[i]['long_memory'].slice((this.currentPage[name]-1)*this.size, this.currentPage[name]*this.size)
          this.totalPage[name] = this.characters[i]['long_memory'].length
      }
    },

    //改变分页页面ID值
    handleCurrentChange(name, val){
      this.currentPage[name] = val
      this.changeCurrentChange()
    },

    //从长期记忆中删除
    removeMemory(name, index){
      var time = this.actions[name][index].time
      var memory = this.actions[name][index].description
      this.actions[name][index].button_hidden = true
      for(var i=0;i<6;i++){
        if(this.characters[i].name==name){
          for(var j=0;j<this.characters[i].long_memory.length;j++){
            if(this.characters[i].long_memory[j].time==time&&this.characters[i].long_memory[j].memory==memory){
              this.characters[i].long_memory.splice(j,1)
              break
            }
          }
          break
        }
      }
      this.changeCurrentChange()
    },

    //添加到长期记忆中
    addMemory(name, index){
      var time = this.actions[name][index].time
      var memory = this.actions[name][index].description
      this.actions[name][index].button_hidden = false
      for(var i=0;i<6;i++){
        if(this.characters[i].name==name){
          var add_memory=[{'time':time, 'memory':memory}]
          this.characters[i].long_memory = add_memory.concat(this.characters[i].long_memory)
        }
      }
      this.changeCurrentChange()
    }
}
}
</script>

<style>
.remove-button:focus{
  color:#909399
}
</style>
