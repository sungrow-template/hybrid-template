import Vue from 'vue'
import VueRouter from 'vue-router'
/**
 * 重写路由的push方法
 */
const routerPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
  return routerPush.call(this, location).catch(error => error)
}
Vue.use(VueRouter)
export const quotechildren = [
  {
    path: '/helloword',
    name: 'helloword',
    label: 'I18N_COMMON_HOMEPAGE',
    component: () => import ('@/pages/HelloWord/helloword.vue'),
    icon: 'el-icon-eleme'
  },
  {
    path: '/ota',
    name: 'OTA',
    label: 'I18N_COMMON_ABOUT',
    component: () => import ('@/pages/OTA/OTA.vue'),
    icon: 'el-icon-eleme'
  }
]

const routes = [
  {
    path: '/',
    redirect: '/helloword',
    name: 'Home',
    children: quotechildren,
    component: () => import ('@/pages/Home.vue')
  }
]

const router = new VueRouter({
  routes
})

export default router
