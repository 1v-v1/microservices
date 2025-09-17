import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
    baseURL: 'http://localhost:8000', // API基础URL
    timeout: 15000, // 请求超时时间
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
service.interceptors.request.use(
    config => {
        // 从本地存储中获取管理员token
        const adminToken = localStorage.getItem('adminToken')
        // 如果token存在，则添加到请求头中
        if (adminToken) {
            config.headers['Authorization'] = `Bearer ${adminToken}`
        }
        return config
    },
    error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {
        const res = response.data
        // 如果返回的状态码不是200，则判断为错误
        if (response.status !== 200) {
            ElMessage({
                message: res.message || '请求错误',
                type: 'error',
                duration: 5 * 1000
            })

            // 如果是401或403，可能是未认证或token过期
            if (response.status === 401 || response.status === 403) {
                // 清除本地token并跳转到登录页
                localStorage.removeItem('adminToken')
                setTimeout(() => {
                    window.location.href = '/#/login'
                }, 1500)
            }

            return Promise.reject(new Error(res.message || '请求错误'))
        } else {
            return res
        }
    },
    error => {
        console.error('响应错误:', error)
        let message = error.message || '请求失败'

        if (error.response) {
            // 请求发出，服务器响应了错误状态
            if (error.response.status === 401 || error.response.status === 403) {
                message = '未授权，请重新登录'
                // 清除本地token并跳转到登录页
                localStorage.removeItem('adminToken')
                setTimeout(() => {
                    window.location.href = '/#/login'
                }, 1500)
            } else if (error.response.data && error.response.data.message) {
                message = error.response.data.message
            }
        } else if (error.request) {
            // 请求发出，但没有收到响应
            message = '服务器无响应，请稍后再试'
        }

        ElMessage({
            message: message,
            type: 'error',
            duration: 5 * 1000
        })

        return Promise.reject(error)
    }
)

export default service 