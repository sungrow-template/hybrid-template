<template>
  <div class="otaUpdate">
    <h4>{{ $t('I18N_COMMON_SOFT_VERSION') }}</h4>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-input v-model="version" :disabled="true" />
      </el-col>
      <el-col :span="8">
        <!-- 检查版本信息和下载时按钮加载，如果下载，按钮中显示文字提示和百分比 -->
        <el-button :loading="buttonLoading || downLoading" type="primary" @click="confirmVersion">
          {{ downLoading ? $t('I18N_COMMON_LOADING_UPDATE') : $t('I18N_COMMON_CHECK_VERSION') }}
          <span v-if="downLoading">{{ downPercentage }}%</span>
        </el-button>
      </el-col>
    </el-row>
    <el-row :gutter="20" class="copyRight">
      <div>{{ $t('I18N_COMMON_CONTACT_US') }}tools@sungrowpower.com</div>
      <div>Copyright © 2020 Sungrow. All rights reserved.</div>
    </el-row>
    <el-dialog :visible.sync="dialogVisible" :close-on-click-modal="false" :title="$t('I18N_COMMON_CHECK_NEW_VERSION')" width="50%" top="calc(50vh - 116px)">
      <div class="msgDisplay">
        <span>{{ $t('I18N_COMMON_LATEST_VERSION') }}</span>
        <div>{{ versionMsg.version_number }}</div>
      </div>
      <div class="msgDisplay">
        <span>{{ $t('I18N_COMMON_SLIDING_VERSION_INFO') }}</span>
        <div>{{ versionMsg.resource_desc }}</div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancleDialogVisible">{{ $t('I18N_COMMON_CANCLE') }}</el-button>
        <el-button type="primary" @click="update">{{ $t('I18N_COMMON_DOWNLOAD') }}</el-button>
      </span>
    </el-dialog>
    <update-dialog />
  </div>
</template>

<script>
import updateDialog from '@/pages/OTA/updateDialog'
import { mapState } from 'vuex'
export default {
  name: 'Ota',
  components: {
    updateDialog
  },
  data() {
    return {
      checkError: {
        401: 'I18N_COMMON_NET_OR_SERVICE',
        402: 'I18N_COMMON_ALREADY_NEW_VERSION'
      }
    }
  },
  computed: {
    ...mapState({
      version: state => state.ota.version
    }),
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
    },
    dialogVisible: {
      get() {
        return this.$store.state.ota.dialogVisible
      },
      set(val) {
        this.$store.commit('SET_DIALOG_VISIABLE', val)
      }
    },
    buttonLoading: {
      get() {
        return this.$store.state.ota.buttonLoading
      },
      set(val) {
        this.$store.commit('SET_BUTTON_LOADING', val)
      }
    }
  },
  methods: {
    confirmVersion() {
      this.buttonLoading = true
      this.$store.dispatch('ota_timer')
      this.$api('ota/get_version', {
        product_code: `${this.version}`
      }).then(res => {
        this.$store.commit('CLEAR_OTA_TIMER')
        this.$store.commit('SET_BUTTON_LOADING', false)
        this.$message.closeAll()
        const { code, data } = res
        if (code === '1') {
          if (data) {
            this.$store.commit('SET_VERSION_MSG', data)
            this.$store.commit('SET_DIALOG_VISIABLE', true)
          } else {
            this.$message.success({ message: this.$t('I18N_COMMON_ALREADY_NEW_VERSION'), duration: 1000 })
            return
          }
        } else {
          this.$message({
            type: code === 402 ? 'success' : 'error',
            message: this.$t(this.checkError[code] || 'I18N_COMMON_NET_OR_SERVICE')
          })
        }
      }).catch(() => {
      }).finally(() => {
        this.$store.commit('SET_BUTTON_LOADING', false)
      })
    },
    update() {
      this.dialogVisible = false
      this.dialogProcess = true
      this.downTitle = 'I18N_COMMON_LOADING_UPDATE' // 正在下载更新
      this.downButtonContent = 'I18N_COMMON_INSTALL'
      this.downLoading = true
      const fs = require('fs')
      const path = `${this.$userPath}\\Download`
      // 检测路径是否存在
      if (!fs.existsSync(path)) {
        fs.mkdirSync(path)
      }
      this.downLoad({ file_path: `${path}\\${this.versionMsg.resource_name}` })
    },
    downLoad(info) {
      this.downPercentage = 0
      this.$api('ota/new_version_download', info, 'post', 200000).catch(() => {})
    },
    cancleDialogVisible() {
      this.$store.commit('SET_DIALOG_VISIABLE', false)
    }
  }
}
</script>

<style lang="scss" scoped>
  .msgDisplay{
    font-size: 14px;
    line-height: 24px;
    margin: 0px;
    padding: 5px 15px;
    display: flex;
    span{
      display: inline-block;
      word-break: break-word;
      width: 100px;
    }
    div{
      flex: 1;
    }
  }
  .exLinksBtns{
    width: 98px;
  }
  .otaUpdate{
    position: relative;
    .copyRight{
      text-align: center;
      position: absolute;
      width: 100%;
      padding-left: 8px;
      bottom: 20px;
    }
    h4{
      margin-top: 30px;
      margin-bottom: 13px;
    }
  }

</style>
