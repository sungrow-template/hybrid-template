<template>
  <div class="home">
    hello word
  </div>
</template>

<script>
export default {
  name: 'Home',
  components: {
  },
  mounted() {
    console.log(this.$electron.remote.app.getPath('userData'))
    console.log(this.$path.join(__dirname, '/'))
  }
}
</script>
