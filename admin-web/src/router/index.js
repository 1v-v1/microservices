import { createRouter, createWebHashHistory } from 'vue-router'

// 路由配置
const routes = [
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/login/index.vue'),
        meta: { title: '管理员登录', requiresAuth: false }
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '极速贷后台管理', requiresAuth: true },
        children: [
            {
                path: '',
                name: 'Home',
                component: () => import('../views/dashboard/home.vue'),
                meta: { title: '首页', requiresAuth: true }
            },
            {
                path: 'users',
                name: 'UserManagement',
                component: () => import('../views/user-management/index.vue'),
                meta: { title: '用户管理', requiresAuth: true }
            },
            {
                path: 'loans',
                name: 'LoanManagement',
                component: () => import('../views/user-management/loans.vue'),
                meta: { title: '贷款管理', requiresAuth: true }
            },
            {
                path: 'repayments',
                name: 'RepaymentManagement',
                component: () => import('../views/user-management/repayments.vue'),
                meta: { title: '还款管理', requiresAuth: true }
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('../views/404.vue')
    }
]

// 创建路由实例
const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
    // 设置页面标题
    document.title = to.meta.title || '极速贷管理系统'

    // 验证是否需要登录权限
    if (to.meta.requiresAuth) {
        // 从localStorage获取认证状态
        const adminToken = localStorage.getItem('adminToken')

        if (adminToken) {
            next() // 已登录，继续导航
        } else {
            // 未登录，重定向到登录页
            next({ name: 'Login', query: { redirect: to.fullPath } })
        }
    } else {
        // 不需要认证的页面直接访问
        next()
    }
})

export default router 