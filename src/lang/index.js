import Vue from 'vue'
import VueI18n from 'vue-i18n'
import locale from 'element-ui/lib/locale'
import elementEnLocale from 'element-ui/lib/locale/lang/en'
import elementZhLocale from 'element-ui/lib/locale/lang/zh-CN'
import zhLocale from './zh_cn'
import enLocale from './en_us'
Vue.use(VueI18n)
const messages = {
  zh_cn: {
    ...elementZhLocale,
    ...zhLocale
  },
  en_us: {
    ...elementEnLocale,
    ...enLocale
  }
}
const i18n = new VueI18n({
  locale: localStorage.getItem('language') || 'zh_cn',
  messages
})

locale.i18n((key, value) => i18n.t(key, value)) // 为了实现element插件的多语言切换
export default i18n
