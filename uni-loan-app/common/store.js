import Vue from 'vue';
import Vuex from 'vuex';
import { storage } from './utils';
import api from './api';

Vue.use(Vuex);

// 用户模块
const userModule = {
    state: {
        token: storage.get('token') || '',
        userInfo: storage.get('userInfo') || null,
        isLogin: !!storage.get('token')
    },
    mutations: {
        SET_TOKEN(state, token) {
            state.token = token;
            storage.set('token', token);
            state.isLogin = !!token;
        },
        SET_USER_INFO(state, userInfo) {
            state.userInfo = userInfo;
            storage.set('userInfo', userInfo);
        },
        UPDATE_USER_INFO(state, userInfo) {
            state.userInfo = { ...state.userInfo, ...userInfo };
            storage.set('userInfo', state.userInfo);
        },
        LOGOUT(state) {
            state.token = '';
            state.userInfo = null;
            state.isLogin = false;
            storage.remove('token');
            storage.remove('userInfo');
        }
    },
    actions: {
        // 登录
        async login({ commit }, data) {
            try {
                const res = await api.user.login(data);
                if (res.message === "登录成功" && res.userInfo) {
                    // 确保用户信息包含username字段
                    const userInfo = {
                        ...res.userInfo,
                        username: data.username  // 保存登录时使用的用户名
                    };

                    // 处理头像URL
                    if (userInfo.avatar && userInfo.avatar.startsWith('/uploads/')) {
                        userInfo.avatar = `http://localhost:8000${userInfo.avatar}`;
                    }

                    // 设置用户信息
                    commit('SET_USER_INFO', userInfo);
                    // 生成一个简单的token (实际项目应该由后端生成)
                    const token = 'token_' + Date.now();
                    commit('SET_TOKEN', token);
                    return Promise.resolve(res);
                } else {
                    return Promise.reject({ message: res.message || "登录失败" });
                }
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 注册
        async register({ commit }, data) {
            try {
                const res = await api.user.register(data);
                return Promise.resolve(res);
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 获取用户信息
        async getUserInfo({ commit, state }) {
            try {
                if (!state.userInfo || !state.userInfo.username) {
                    return Promise.reject({ message: "用户未登录" });
                }
                const res = await api.user.getUserInfo(state.userInfo.username);
                if (res.userInfo) {
                    // 处理头像URL
                    const userInfo = { ...res.userInfo };
                    if (userInfo.avatar && userInfo.avatar.startsWith('/uploads/')) {
                        userInfo.avatar = `http://localhost:8000${userInfo.avatar}`;
                    }

                    commit('SET_USER_INFO', userInfo);
                    return Promise.resolve(userInfo);
                } else {
                    return Promise.reject({ message: "获取用户信息失败" });
                }
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 退出登录
        logout({ commit }) {
            commit('LOGOUT');
            uni.reLaunch({
                url: '/pages/login/login'
            });
        },

        // 更新用户资料
        async updateUserProfile({ commit, state }, profileData) {
            try {
                if (!state.userInfo || !state.userInfo.username) {
                    return Promise.reject({ message: "用户未登录" });
                }

                // 添加用户名到资料数据
                const data = {
                    ...profileData,
                    username: state.userInfo.username
                };

                // 调用API更新用户资料
                const res = await api.user.updateProfile(data);

                // 更新本地用户信息
                if (res.message === "个人资料更新成功") {
                    // 重新获取用户信息
                    await this.dispatch('user/getUserInfo');
                    return Promise.resolve(res);
                } else {
                    return Promise.reject({ message: res.message || "更新资料失败" });
                }
            } catch (error) {
                return Promise.reject(error);
            }
        }
    }
};

// 借款模块
const loanModule = {
    state: {
        loanLimit: {
            total: 0,
            used: 0,
            available: 0
        },
        loanRecords: []
    },
    mutations: {
        SET_LOAN_LIMIT(state, data) {
            state.loanLimit = data;
        },
        SET_LOAN_RECORDS(state, records) {
            state.loanRecords = records;
        }
    },
    actions: {
        // 获取借款额度
        async getLoanLimit({ commit, rootState }) {
            try {
                const username = rootState.user.userInfo?.username;
                if (!username) {
                    return Promise.reject({ message: "用户未登录" });
                }

                const res = await api.borrow.getLoanLimit(username);
                commit('SET_LOAN_LIMIT', res);
                return Promise.resolve(res);
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 申请借款
        async applyLoan({ rootState }, loanData) {
            try {
                const username = rootState.user.userInfo?.username;
                if (!username) {
                    return Promise.reject({ message: "用户未登录" });
                }

                const data = {
                    username,
                    amount: loanData.amount,
                    term: loanData.term,
                    repayMethod: loanData.repayType || 'equal-installment'
                };

                const res = await api.borrow.applyLoan(data);
                return Promise.resolve(res);
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 获取借款记录
        async getLoanRecords({ commit, rootState }) {
            try {
                const username = rootState.user.userInfo?.username;
                if (!username) {
                    return Promise.reject({ message: "用户未登录" });
                }

                const records = await api.borrow.getLoanRecords(username);
                commit('SET_LOAN_RECORDS', records);
                return Promise.resolve(records);
            } catch (error) {
                return Promise.reject(error);
            }
        }
    }
};

// 还款模块
const repayModule = {
    state: {
        repayList: [],
        totalRepayAmount: 0,
        repaymentHistory: []
    },
    mutations: {
        SET_REPAY_LIST(state, list) {
            state.repayList = list;
            // 计算总待还金额
            state.totalRepayAmount = list.reduce((sum, item) => sum + parseFloat(item.amount), 0);
        },
        SET_REPAYMENT_HISTORY(state, history) {
            state.repaymentHistory = history;
        }
    },
    actions: {
        // 获取待还款列表
        async getRepayList({ commit, rootState }) {
            try {
                const username = rootState.user.userInfo?.username;
                if (!username) {
                    return Promise.reject({ message: "用户未登录" });
                }

                const res = await api.repay.getRepayList(username);
                commit('SET_REPAY_LIST', res);
                return Promise.resolve(res);
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 提交还款
        async submitRepay({ commit, dispatch, rootState }, repayData) {
            try {
                // 获取用户名 - 多种方式尝试
                let username = null;
                const userInfo = rootState.user.userInfo;

                if (userInfo) {
                    username = userInfo.username || userInfo.realName || userInfo.name;
                }

                // 如果还是没有用户名，尝试从本地存储获取
                if (!username) {
                    const storedUserInfo = uni.getStorageSync('userInfo');
                    if (storedUserInfo) {
                        if (typeof storedUserInfo === 'string') {
                            try {
                                const parsedUserInfo = JSON.parse(storedUserInfo);
                                username = parsedUserInfo.username || parsedUserInfo.realName || parsedUserInfo.name;
                            } catch (e) {
                                username = storedUserInfo;
                            }
                        } else if (typeof storedUserInfo === 'object') {
                            username = storedUserInfo.username || storedUserInfo.realName || storedUserInfo.name;
                        }
                    }
                }

                if (!username) {
                    return Promise.reject({ message: "用户信息不存在，请重新登录" });
                }

                // 支持分期还款的数据结构
                const data = {
                    username,
                    loan_id: repayData.loanId,
                    amount: repayData.amount,
                    periods: repayData.periods || 1, // 还款期数
                    payment_method: repayData.paymentMethod || 'alipay', // 支付方式
                    repayment_plan: repayData.repaymentPlan || [] // 还款计划
                };

                console.log('提交分期还款数据:', data);
                const res = await api.repay.submitRepay(data);

                // 更新还款列表和用户信息
                await dispatch('getRepayList');
                await dispatch('user/getUserInfo', null, { root: true });

                return Promise.resolve(res);
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 获取还款记录
        async getRepaymentHistory({ commit, rootState }) {
            try {
                const username = rootState.user.userInfo?.username;
                if (!username) {
                    return Promise.reject({ message: "用户未登录" });
                }

                const history = await api.repay.getRepayHistory(username);
                commit('SET_REPAYMENT_HISTORY', history);
                return Promise.resolve(history);
            } catch (error) {
                return Promise.reject(error);
            }
        },

        // 获取还款计划
        async getRepayPlan({ rootState }, loanId) {
            try {
                const username = rootState.user.userInfo?.username;
                if (!username) {
                    return Promise.reject({ message: "用户未登录" });
                }

                const plan = await api.repay.getRepayPlan(loanId, username);
                return Promise.resolve(plan);
            } catch (error) {
                return Promise.reject(error);
            }
        }
    }
};

export default new Vuex.Store({
    modules: {
        user: {
            namespaced: true,
            ...userModule
        },
        loan: {
            namespaced: true,
            ...loanModule
        },
        repay: {
            namespaced: true,
            ...repayModule
        }
    }
}); 