<template>
  <div class="side-bar">
    <el-menu :default-active="$route.path">
      <template v-for="(item, index) in menuList">
        <el-menu-item :key="index" :title="$t(item.label)" :index="item.path" @click="toRouter(item)">
          <i :class="item.icon" />
          <span>{{ $t(item.label) }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script>
import { quotechildren } from '@/router/index.js'
export default {
  data() {
    return {
      menuList: quotechildren
    }
  },
  methods: {
    toRouter(item) {
      this.$router.push(item.path)
    }
  }
}
</script>

<style lang="scss">
@import '@/styles/sidebar.scss';
</style>
