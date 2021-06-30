<template>
  <div class="home-page">
    <top-bar />
    <div
      v-loading.lock="fullLoading"
      :element-loading-text="loadingText"
      class="home-main"
      element-loading-spinner="el-icon-loading"
      element-loading-background="rgba(0, 0, 0, 0.5)"
    >
      <side-bar />
      <keep-alive>
        <router-view class="app-main" />
      </keep-alive>
    </div>
  </div>
</template>

<script>
import TopBar from '_c/Home/TopBar'
import SideBar from '_c/Home/SideBar'
import { mapState } from 'vuex'
export default {
  components: {
    TopBar,
    SideBar
  },
  computed: {
    ...mapState({
      fullLoading: state => state.app.fullLoading,
      loadingText: state => state.app.loadingText
    })
  },
  mounted() {
    window.addEventListener('keyup', (event) => {
      if (event.code === 'F12') {
        this.$electron.remote.getCurrentWebContents().toggleDevTools()
      }
    })
  }
}
</script>
<style lang="scss" scoped>
.home-page{
  height: 100%;
  position: relative;
  display: flex;
  padding-top: 1px;
  flex-direction: column;
  .home-main{
    height: 0;
    flex: 1;
    display: flex;
    flex-direction: row;
  }
  .app-main{
    width: 0;
    flex: 1;
    padding: 10px;
    height: 100%;
  }
}
</style>
