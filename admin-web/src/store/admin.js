import { defineStore } from 'pinia'
import { adminLogin } from '../api/admin'
import { ElMessage } from 'element-plus'

export const useAdminStore = defineStore('admin', {
    state: () => ({
        token: localStorage.getItem('adminToken') || '',
        adminInfo: JSON.parse(localStorage.getItem('adminInfo') || '{}'),
        loading: false
    }),

    getters: {
        isLoggedIn: (state) => !!state.token
    },

    actions: {
        // 管理员登录
        async login(credentials) {
            this.loading = true
            try {
                const response = await adminLogin(credentials)
                if (response.token) {
                    this.token = response.token
                    this.adminInfo = response.adminInfo || {}

                    // 存储到localStorage
                    localStorage.setItem('adminToken', response.token)
                    localStorage.setItem('adminInfo', JSON.stringify(this.adminInfo))

                    ElMessage({
                        type: 'success',
                        message: '登录成功'
                    })

                    return true
                }
                return false
            } catch (error) {
                console.error('登录失败:', error)
                ElMessage({
                    type: 'error',
                    message: error.message || '登录失败，请检查用户名和密码'
                })
                return false
            } finally {
                this.loading = false
            }
        },

        // 退出登录
        logout() {
            this.token = ''
            this.adminInfo = {}

            // 清除localStorage
            localStorage.removeItem('adminToken')
            localStorage.removeItem('adminInfo')

            // 重定向到登录页
            window.location.href = '/#/login'
        }
    }
}) 