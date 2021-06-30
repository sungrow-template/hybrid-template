<template>
  <div class="top-bar">
    <div class="title">
      <img :src="require('@/assets/logo.png')" alt="">
      项目名
    </div>
    <div class="bar-right">
      <el-popover
        placement="bottom"
        width="60"
        trigger="hover"
      >
        <button slot="reference" class="minbt switchLang">
          <img :src="require('@/assets/lang.svg')">
          <span>{{ languageName }}</span>
        </button>
        <div class="lang-item" @click="switchLang('zh_cn')">
          简体中文
        </div>
        <div class="lang-item white-border" @click="switchLang('en_us')">
          English
        </div>
      </el-popover>
      <button class="minbt" @click="min">
        <i class="el-icon-minus" />
      </button>
      <button class="maxbt" @click="max">
        <i v-if="winNormal" class="el-icon-copy-document" />
        <i v-else class="el-icon-full-screen" />
      </button>
      <button class="closebt" @click="close">
        <i class="el-icon-close" />
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopBar',
  data() {
    return {
      winNormal: false // 非全屏
    }
  },
  computed: {
    language: {
      get() {
        return this.$store.state.app.language
      },
      set(lang) {
        this.$store.commit('SET_LANGUAGE', lang)
      }
    },
    languageName() {
      return this.language === 'zh_cn' ? '简体中文' : 'English'
    }
  },
  mounted() {
    this.winNormal = this.$electron.remote.getCurrentWindow().isMaximized()
    window.addEventListener('resize', () => {
      this.winNormal = this.$electron.remote.getCurrentWindow().isMaximized()
    })
  },
  methods: {
    close() {
      this.$electron.ipcRenderer.send('app-close')
    },
    min() {
      this.$electron.ipcRenderer.send('app-min')
    },
    max() {
      this.winNormal = !this.$electron.remote.getCurrentWindow().isMaximized()
      this.$electron.ipcRenderer.send('app-max')
    },
    switchLang(lang) {
      this.$i18n.locale = lang
      this.language = lang
    }
  }
}
</script>

<style lang="scss" scoped>
.top-bar {
  width: 100%;
  height: 30px;
  line-height: 30px;
  display: flex;
  justify-content: space-between;
  -webkit-app-region: drag;
  -webkit-user-select: none;
  border-bottom: 1px solid #d9d9d9;
}
.title{
  padding-left: 10px;
  line-height: 30px;
  font-size: 14px;
  text-align: center;
  display: flex;
  img{
    width: 20px;
    height: 20px;
    margin-top: 5px;
    margin-right: 5px;
  }
}
button{
  padding: 0px;
  margin: 0px;
  width: 46px;
  height: 30px;
  background-repeat: no-repeat;
  background-color: transparent;
  border: none;
  background-position: center;
  -webkit-app-region: no-drag;
  outline: none;
  transition: all .3s;
  color: #333;
}
.switchLang{
  font-size: 14px;
  width: auto;
  height: 100%;
  line-height: 30px;
  display: inline-flex;
  padding: 0 4px;
  img{
    width: 20px;
    height: 20px;
    margin: 5px 5px 0 0;
    vertical-align: top;
  }
  i{
    margin: 5px 5px 0 0;
    vertical-align: top;
    font-size: 20px;
    color: #409EFF;
  }
  &:hover{
    background-color: #D0D2D5;
  }
}
.switchLang:hover{
  background-color: #D0D2D5;
}
.minbt, .maxbt{
  &:hover{
    background-color: #D0D2D5;
  }
}
.closebt:hover{
  background-color: #E81123;
  color: white;
}
.bar-right{
  display: flex;
  line-height: 30px;
}
</style>
