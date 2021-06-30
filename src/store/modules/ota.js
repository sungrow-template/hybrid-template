import { Message } from 'element-ui'
import i18n from '@/lang'
const state = {
  versionMsg: { version_number: '', resource_desc: '' },
  downTitle: 'I18N_COMMON_LOADING_UPDATE',
  downButtonContent: 'I18N_COMMON_INSTALL',
  downLoading: false,
  downPercentage: 0,
  dialogProcess: false,
  buttonLoading: false,
  dialogVisible: false,
  otaNumber: 0,
  otaTimer: null, // 定时器
  version: 'v1.0.0.0'
}

const actions = {
  ota({ commit }, info) {
    const { flag, code, procss } = info
    if (flag === '1') {
      commit('SET_PERCENTAGE', '100')
      // 增加延迟，防止exe尾缀未修改完
      setTimeout(() => {
        commit('SET_DOWNLOADING', false)
        commit('SET_DIALOG_PROCESS', true)
      }, 2000)
    } else {
      if (code === '0') { // 下载失败提示
        Message.closeAll()
        commit('SET_DOWNLOADING', false)
        commit('SET_DOWN_TITLE', 'I18N_COMMON_NOTIFICATION_DOWNLOAD_ERROR')
        commit('SET_DOWN_BUTTON_CONTENT', 'I18N_COMMON_DETERMINE')
      } else { // 获取进度条进度
        commit('SET_PERCENTAGE', procss)
      }
    }
  },
  // 防止ota升级接口10s内未回复导致超时问题
  ota_timer({ state, commit }) {
    if (state.otaTimer) commit('CLEAR_OTA_TIMER')
    state.otaTimer = setInterval(() => {
      state.otaNumber += 1
      if (state.otaNumber > 10) {
        commit('CLEAR_OTA_TIMER')
        commit('SET_BUTTON_LOADING', false)
        Message.error(i18n.t('I18N_COMMON_REQUEST_TIMEOUT'))
      }
    }, 1000)
  }
}

const mutations = {
  // 版本信息
  SET_VERSION_MSG(state, val) {
    state.versionMsg = val
  },
  // 下载弹框标题
  SET_DOWN_TITLE(state, val) {
    state.downTitle = val
  },
  // 下载加载
  SET_DOWNLOADING(state, val) {
    state.downLoading = val
  },
  // 进度条
  SET_PERCENTAGE(state, val) {
    state.downPercentage = parseInt(val)
  },
  // 下载进度条弹框
  SET_DIALOG_PROCESS(state, val) {
    state.dialogProcess = val
  },
  // 下载失败按钮信息
  SET_DOWN_BUTTON_CONTENT(state, val) {
    state.downButtonContent = val
  },
  // 按钮加载
  SET_BUTTON_LOADING(state, val) {
    state.buttonLoading = val
  },
  // 弹框显示
  SET_DIALOG_VISIABLE(state, val) {
    state.dialogVisible = val
  },
  // 清除定时器
  CLEAR_OTA_TIMER(state) {
    window.clearInterval(state.otaTimer)
    state.otaNumber = 0
    state.otaTimer = null
  }
}

export default {
  state,
  actions,
  mutations
}
