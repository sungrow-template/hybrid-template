const state = {
  // 默认语言为中文
  language: localStorage.getItem('language') || 'zh_cn',
  fullLoading: false,
  loadingText: '加载中'
}

const actions = {
}

const mutations = {
  // 设置语言
  SET_LANGUAGE: (state, language) => {
    state.language = language
    localStorage.setItem('language', language)
  },
  SET_FULL_LOADING(state, val) {
    state.fullLoading = val
  },
  SET_LOADING_TEXT(state, val) {
    state.loadingText = val
  }
}

export default {
  state,
  mutations,
  actions
}
