import App from './App'

// #ifndef VUE3
import Vue from 'vue'
Vue.config.productionTip = false

// 引入uniapp UI组件
import uniIcons from '@/uni_modules/uni-icons/components/uni-icons/uni-icons.vue'
Vue.component('uni-icons', uniIcons)

// 引入Vuex store
import store from './common/store'

App.mpType = 'app'
const app = new Vue({
    ...App,
    store
})
app.$mount()
// #endif

// #ifdef VUE3
import { createSSRApp } from 'vue'
export function createApp() {
    const app = createSSRApp(App)
    return {
        app
    }
}
// #endif 