import Vue from 'vue'
import axios from 'axios'
import { Message } from 'element-ui'
import store from '@/store'
// 引入子进程
const { spawn, exec } = require('child_process')
const { remote, ipcRenderer } = require('electron')
// 获取当前环境
const NODE_ENV = process.env.NODE_ENV
// 获取electron的remote路径 及 用户数据路径
const remotePath = remote.getGlobal('path')
// 启动python程序
let ps = null
let port = '8081'
function startPython(api_name, api_data) {
  if (NODE_ENV === 'development') {
    // 开发模式启动main.py
    ps = spawn(`C:\\Users\\yaokunlun\\Desktop\\sungrow\\baseframework\\py\\venv\\Scripts\\python.exe`, [`${remotePath}/py/main.py`, '[]'])
  } else {
    // 生产模式调用copy后的exe地址
    ps = spawn(`${remotePath}\\dist\\main\\main.exe`, ['[]'])
  }
  // 正常日志数据返回
  ps.stdout.on('data', (data) => {
    const res = data.toString()
    try {
      console.log({ type: 'python-stdout', res })
      // 设置python的pid独立出来
      if (res.indexOf('set-info') > -1) {
        const str = JSON.parse(res)
        ipcRenderer.send('set-python-pid', str.pid)
        port = str.port
      }
      if (res.indexOf('ota') > -1) {
        let info = {}
        if (res.indexOf('}{') > -1) {
          const str = res.split('}{')
          info = JSON.parse(`{${str[str.length - 1]}`)
        } else {
          info = JSON.parse(res)
        }
        store.dispatch('ota', info)
        return
      }
    } catch (error) {
      console.error({ type: 'python-error-stdout', res })
    }
  })
  // 错误日志返回
  ps.stderr.on('data', (data) => {
    const res = data.toString()
    try {
      console.error({ type: 'python-stderr', res })
    } catch (error) {
      console.error({ type: 'python-stderr-error', res })
    }
  })
}
startPython()
// 初始化axios
const instance = axios.create({
  // baseURL: `http://127.0.0.1`, // 默认请求地址
  timeout: 10000, // 超时时间 1000 = 1s
  headers: { 'Content-Type': 'application/json' }
})
instance.interceptors.response.use(response => {
  // 对响应数据做点什么
  return response.data.result_data
}, error => {
  // 对响应错误做点什么
  if (error.code === 'ECONNABORTED' && error.message.indexOf('timeout') !== -1) {
    Message.closeAll()
    Message.error('请求超时')
    return Promise.reject('请求超时')
  }
  return Promise.reject(error)
})
export function api(url, data, method = 'post', timeout = 10000) {
  return instance({ url: `http://127.0.0.1:${port}/${url}`, data, method, timeout: timeout })
}
// 另存为事件
const ipc2promise = require('ipc2promise')
function save(info) {
  return new Promise((resovle, reject) => {
    ipc2promise.send('save-dialog', info).then(res => {
      resovle(res)
    }).catch(() => {
      reject()
    })
  })
}
// 挂载到Vue实例上
Vue.prototype.$api = api
Vue.prototype.$save = save
Vue.prototype.$exec = exec
Vue.prototype.$spawn = spawn
