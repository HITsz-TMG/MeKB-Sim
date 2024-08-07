import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.use(ElementUI)


new Vue({
  render: h => h(App),
  data(){
    return {
      backendServer:'http://xxxxxx:7040',
    }
  },
}).$mount('#app')
