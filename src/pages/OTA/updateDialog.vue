<template>
  <el-dialog :visible.sync="dialogProcess" modal-append-to-body :title="$t(downTitle)" :close-on-click-modal="false" :before-close="closeDialog" width="50%" top="calc(50vh - 116px)">
    <el-progress :text-inside="true" :stroke-width="20" :percentage="downPercentage" status="exception" />
    <span slot="footer" class="dialog-footer">
      <el-button :loading="downLoading || installLoading" type="primary" @click="installExe">{{ $t(downButtonContent) }}</el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  data() {
    return {
      installLoading: false
    }
  },
  computed: {
    versionMsg: {
      get() {
        return this.$store.state.ota.versionMsg
      },
      set(val) {
        this.$store.commit('SET_VERSION_MSG', val)
      }
    },
    downTitle: {
      get() {
        return this.$store.state.ota.downTitle
      },
      set(val) {
        this.$store.commit('SET_DOWN_TITLE', val)
      }
    },
    dialogProcess: {
      get() {
        return this.$store.state.ota.dialogProcess
      },
      set(val) {
        this.$store.commit('SET_DIALOG_PROCESS', val)
      }
    },
    downLoading: {
      get() {
        return this.$store.state.ota.downLoading
      },
      set(val) {
        this.$store.commit('SET_DOWNLOADING', val)
      }
    },
    downPercentage: {
      get() {
        return this.$store.state.ota.downPercentage
      },
      set(val) {
        this.$store.commit('SET_PERCENTAGE', val)
      }
    },
    downButtonContent: {
      get() {
        return this.$store.state.ota.downButtonContent
      },
      set(val) {
        this.$store.commit('SET_DOWN_BUTTON_CONTENT', val)
      }
    }
  },
  mounted() {
  },
  methods: {
    closeDialog() {
      this.dialogProcess = false
    },
    // 安装下载的包
    installExe() {
      if (this.downTitle === 'I18N_COMMON_NOTIFICATION_DOWNLOAD_ERROR') {
        this.downPercentage = 0
        this.dialogProcess = false
        return
      }
      const path = `${this.$userPath}\\Download\\${this.versionMsg.resource_name}`
      const fs = require('fs')
      if (fs.existsSync(path)) {
        this.installStart(path)
      } else {
        setTimeout(() => {
          if (fs.existsSync(path)) {
            this.installStart(path)
          } else {
            this.$message.error('未找到安装包文件,请再试一次或重新下载更新')
          }
        }, 1000)
      }
    },
    installStart(path) {
      try {
        this.installLoading = true
        const subprocess = this.$spawn(path, ['child_program.js'], {
          detached: true,
          stdio: 'ignore'
        })
        subprocess.unref()
        setTimeout(() => {
          this.$electron.ipcRenderer.send('app-close')
        }, 300)
      } catch (error) {
        this.installLoading = false
        this.$message.closeAll()
        this.$message.error(this.$t('I18N_COMMON_OPERATE_FAILURE'))
      }
    }
  }
}
</script>
<style lang="scss" scoped>
.error-info{
  height: calc(80vh - 184px);
  overflow: auto;
}
</style>
