import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
// 初始化css样式
import 'normalize.css/normalize.css'
// element-ui 样式
import '@/styles/element-variables.scss'
// 默认全局样式
import '@/styles/index.scss'
// 国际化
import i18n from './lang'
// 引入要初始化的js
import '@/utils/api'
import ElementUI from 'element-ui'
Vue.use(ElementUI)
// 挂载electron到vue实例上
const electron = require('electron')
Vue.prototype.$electron = electron
// 挂载path到vue实例上 (使用时path将会基于项目目录)
Vue.prototype.$path = electron.remote.getGlobal('path')
// 用户数据目录
Vue.prototype.$userPath = electron.remote.app.getPath('userData')

Vue.config.productionTip = false

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
