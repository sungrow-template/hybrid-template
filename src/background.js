'use strict'

import { app, protocol, BrowserWindow, Menu, ipcMain, dialog } from 'electron'
import {
  createProtocol
  // installVueDevtools
} from 'vue-cli-plugin-electron-builder/lib'

const isDevelopment = process.env.NODE_ENV !== 'production'

let win

protocol.registerSchemesAsPrivileged([{ scheme: 'app', privileges: { secure: true, standard: true }}])

// 记录Python进程id 在关闭窗口时Kill
let pythonPid = ''
function killPython() {
  process.kill(pythonPid)
}

function createWindow() {
  // Create the browser window.
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    // 隐藏系统自带框架
    frame: false,
    webPreferences: {
      webSecurity: false,
      nodeIntegration: true
    }
    // __static对应public目录
    // icon: `${__static}/app.ico`
  })

  // 打包后是否打开调试工具
  // win.webContents.openDevTools()

  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Load the url of the dev server if in development mode
    win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    if (!process.env.IS_TEST) win.webContents.openDevTools()
  } else {
    createProtocol('app')
    // Load the index.html when not in development
    win.loadURL('app://./index.html')
  }
  win.on('close', () => {
    killPython()
  })
  win.on('closed', () => {
    win = null
  })
  createMenu()
}

// 菜单栏设置
function createMenu() {
  // windows及linux系统
  Menu.setApplicationMenu(null)
}

// 关闭程序
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (win === null) {
    createWindow()
  }
})

app.on('ready', async() => {
  if (isDevelopment && !process.env.IS_TEST) {
    // 安装vue调试工具 （有科学VPN的情况建议安装，否则需要等待）
    // try {
    //   await installVueDevtools()
    // } catch (e) {
    //   console.error('Vue Devtools failed to install:', e.toString())
    // }
  }
  createWindow()
})
// 当前项目路径
const path = require('path')
global['path'] = path.join(__dirname, '..')

if (isDevelopment) {
  if (process.platform === 'win32') {
    process.on('message', data => {
      if (data === 'graceful-exit') {
        app.quit()
      }
    })
  } else {
    process.on('SIGTERM', () => {
      app.quit()
    })
  }
}
// 获取python的后台id
ipcMain.on('set-python-pid', (event, val) => {
  pythonPid = val
})
// 关闭
ipcMain.on('app-close', () => {
  win.close()
})
// 最大化
ipcMain.on('app-max', () => {
  if (win.isMaximized()) {
    win.unmaximize()
  } else {
    win.maximize()
  }
})
// 最小化
ipcMain.on('app-min', () => {
  win.minimize()
})
// 另存为事件
const ipc2promise = require('ipc2promise')
ipc2promise.on('save-dialog', async(event, info, resolve, reject) => {
  const { name, extensions, title } = info
  dialog.showSaveDialog({
    title: '另存为',
    defaultPath: title,
    filters: [
      { name, extensions }
    ]
  }, (filename) => {
    if (filename) {
      resolve(filename)
    } else {
      reject()
    }
  })
})
