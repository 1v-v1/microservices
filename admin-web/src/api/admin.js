import request from './request'

// 管理员登录
export function adminLogin(data) {
    return request({
        url: '/admin/login',
        method: 'post',
        data
    })
}

// 获取所有用户列表
export function getUsersList() {
    return request({
        url: '/admin/users',
        method: 'get'
    })
}

// 获取单个用户详情
export function getUserDetail(username) {
    return request({
        url: `/admin/users/${username}`,
        method: 'get'
    })
}

// 更新用户信息
export function updateUser(username, data) {
    return request({
        url: `/admin/users/${username}`,
        method: 'put',
        data
    })
}

// 删除用户
export function deleteUser(username) {
    return request({
        url: `/admin/users/${username}`,
        method: 'delete'
    })
}

// 获取所有贷款列表
export function getLoansList() {
    return request({
        url: '/admin/loans',
        method: 'get'
    })
}

// 审批贷款
export function approveLoan(loanId, data) {
    return request({
        url: `/admin/loans/${loanId}/approve`,
        method: 'post',
        data
    })
}

// 获取所有还款记录
export function getRepaymentsList() {
    return request({
        url: '/admin/repayments',
        method: 'get'
    })
}

// 统计数据接口
export function getStatistics() {
    return request({
        url: '/admin/statistics',
        method: 'get'
    })
}

// 导出用户数据
export function exportUsers() {
    return request({
        url: '/admin/export/users',
        method: 'get',
        responseType: 'blob'
    })
}

// 导出贷款数据
export function exportLoans() {
    return request({
        url: '/admin/export/loans',
        method: 'get',
        responseType: 'blob'
    })
}

// 导出还款数据
export function exportRepayments() {
    return request({
        url: '/admin/export/repayments',
        method: 'get',
        responseType: 'blob'
    })
} 