// API接口统一管理
const BASE_URL = 'http://localhost:8000';
const IS_MOCK = false; // 使用真实接口

// 模拟数据
const mockData = {
    // 用户相关
    '/user/login': {
        token: 'mock_token_123456',
        userInfo: {
            name: '张先生',
            id: '3608745',
            phone: '13800138000',
            avatar: '',
            creditScore: 720,
            creditLevel: '良好',
            loanLimit: 50000,
            totalBorrowed: 20000,
            pendingRepay: 10000
        }
    },
    '/user/info': {
        name: '张先生',
        id: '3608745',
        phone: '13800138000',
        avatar: '',
        creditScore: 720,
        creditLevel: '良好',
        loanLimit: 50000,
        totalBorrowed: 20000,
        pendingRepay: 10000
    },
    // 借款相关
    '/loan/limit': {
        total: 50000,
        used: 10000,
        available: 40000
    },
    '/loan/records': [
        {
            id: '1001',
            amount: 5000,
            interest: 250,
            term: 6,
            status: 'repaying',
            applyDate: '2023-06-10',
            approveDate: '2023-06-11'
        },
        {
            id: '1002',
            amount: 10000,
            interest: 500,
            term: 12,
            status: 'completed',
            applyDate: '2023-03-15',
            approveDate: '2023-03-16'
        }
    ],
    // 还款相关
    '/repay/list': [
        {
            id: '2001',
            title: '消费贷款',
            amount: 1000,
            dueDate: '2023-07-15'
        },
        {
            id: '2002',
            title: '信用借款',
            amount: 3000,
            dueDate: '2023-07-28'
        }
    ],
    '/repay/plan': [
        {
            month: 1,
            amount: 1000,
            interest: 50,
            dueDate: '2023-07-15'
        },
        {
            month: 2,
            amount: 1000,
            interest: 50,
            dueDate: '2023-08-15'
        }
    ]
};

// 封装请求方法
const request = (url, method = 'GET', data = {}, header = {}) => {
    return new Promise((resolve, reject) => {
        // 使用模拟数据
        if (IS_MOCK) {
            setTimeout(() => {
                // 根据URL返回对应的模拟数据
                const mockResponse = mockData[url];
                if (mockResponse) {
                    resolve(mockResponse);
                } else {
                    reject({ message: '未找到模拟数据' });
                }
            }, 500); // 模拟网络延迟
            return;
        }

        // 真实网络请求
        console.log('API请求:', {
            url: BASE_URL + url,
            method,
            data,
            header: {
                'content-type': 'application/json',
                ...header
            }
        });

        uni.request({
            url: BASE_URL + url,
            method,
            data,
            header: {
                'content-type': 'application/json',
                ...header
            },
            success: (res) => {
                console.log('API响应:', res);
                if (res.statusCode === 200) {
                    // 后端接口返回格式调整为直接返回数据
                    resolve(res.data);
                } else {
                    console.error('API错误:', res);
                    const errorMsg = res.data?.message || '网络错误';
                    uni.showToast({
                        title: errorMsg,
                        icon: 'none'
                    });
                    reject(res.data || { message: errorMsg });
                }
            },
            fail: (err) => {
                console.error('网络请求失败:', err);
                uni.showToast({
                    title: '网络连接失败',
                    icon: 'none'
                });
                reject(err);
            }
        });
    });
};

// 用户相关接口
const userApi = {
    // 用户登录
    login(data) {
        return request('/login', 'POST', data);
    },

    // 用户注册
    register(data) {
        return request('/register', 'POST', data);
    },

    // 更新用户资料
    updateProfile(data) {
        return request('/user/profile', 'POST', data);
    },

    // 获取用户信息
    getUserInfo(username) {
        return request('/user/info', 'GET', { username });
    }
};

// 借款相关接口
const borrowApi = {
    // 获取借款额度
    getLoanLimit(username) {
        return request('/user/info', 'GET', { username }).then(res => {
            if (res.userInfo) {
                return {
                    total: parseFloat(res.userInfo.loanLimit) || 0,
                    used: parseFloat(res.userInfo.pendingRepay) || 0,
                    available: parseFloat(res.userInfo.loanLimit) - parseFloat(res.userInfo.pendingRepay) || 0
                };
            }
            return { total: 0, used: 0, available: 0 };
        });
    },

    // 提交借款申请
    applyLoan(data) {
        // 确保传递还款方式参数
        const loanData = {
            username: data.username,
            loan_amount: data.amount,
            loan_term: data.term,
            repay_method: data.repayMethod || 'equal-installment' // 使用前端传入的还款方式，默认等额本息
        };
        return request('/loan/apply', 'POST', loanData);
    },

    // 获取借款记录
    getLoanRecords(username) {
        return request('/loan/list', 'GET', { username }).then(res => {
            if (res.loans) {
                return res.loans.map(loan => ({
                    id: loan.loan_id,
                    title: '贷款',
                    amount: parseFloat(loan.loan_amount),
                    interest: parseFloat(loan.interest_rate),
                    term: parseInt(loan.loan_term),
                    status: loan.status,
                    applyDate: loan.apply_date,
                    approveDate: loan.approve_date,
                    remainingAmount: parseFloat(loan.remaining_amount),
                    monthlyPayment: parseFloat(loan.monthly_payment),
                    dueDate: loan.next_payment_date
                }));
            }
            return [];
        });
    }
};

// 还款相关接口
const repayApi = {
    // 获取待还款列表
    getRepayList(username) {
        return request('/loan/list', 'GET', { username }).then(res => {
            if (res.loans) {
                return res.loans.filter(loan => loan.status === 'approved' && parseFloat(loan.remaining_amount) > 0)
                    .map(loan => {
                        // 计算距离到期日的天数
                        const dueDate = loan.next_payment_date;
                        const today = new Date();
                        const dueDateTime = new Date(dueDate);
                        const diffTime = dueDateTime - today;
                        const daysToExpire = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

                        return {
                            id: loan.loan_id,
                            title: '贷款待还',
                            amount: parseFloat(loan.remaining_amount),
                            dueDate: loan.next_payment_date,
                            monthlyPayment: parseFloat(loan.monthly_payment),
                            daysToExpire: daysToExpire
                        };
                    });
            }
            return [];
        });
    },

    // 提交还款
    submitRepay(data) {
        return request('/loan/repay', 'POST', data);
    },

    // 获取还款记录
    getRepayHistory(username) {
        return request('/repayment/list', 'GET', { username }).then(res => {
            if (res.repayments) {
                return res.repayments.map(repay => ({
                    id: repay.repayment_id,
                    loanId: repay.loan_id,
                    amount: parseFloat(repay.amount),
                    paymentDate: repay.payment_date,
                    status: repay.status
                }));
            }
            return [];
        });
    },

    // 获取还款计划
    getRepayPlan(loanId, username) {
        return request('/loan/list', 'GET', { username }).then(res => {
            if (res.loans) {
                const loan = res.loans.find(l => l.loan_id === loanId);
                if (loan) {
                    const monthlyPayment = parseFloat(loan.monthly_payment);
                    const term = parseInt(loan.loan_term);
                    const interestRate = parseFloat(loan.interest_rate) / 100; // 年利率转为小数
                    const annualInterestRate = interestRate;
                    const loanAmount = parseFloat(loan.loan_amount);
                    const repayMethod = loan.repay_method || 'equal-installment'; // 获取还款方式，默认等额本息

                    // 短期贷款（31天及以下）一次性还款
                    if (term <= 31) {
                        const dailyRate = annualInterestRate / 365;
                        const totalInterest = loanAmount * dailyRate * term;
                        const totalAmount = loanAmount + totalInterest;

                        const applyDate = new Date(loan.apply_date);
                        const dueDate = new Date(applyDate);
                        dueDate.setDate(dueDate.getDate() + term);

                        // 短期贷款只有一期
                        return [{
                            period: 1,
                            month: 1,
                            amount: totalAmount,
                            principal: loanAmount,
                            interest: totalInterest,
                            dueDate: dueDate.toISOString().split('T')[0],
                            remainingPrincipal: 0
                        }];
                    }

                    // 确定实际月数
                    let months = term;
                    if (term === 90) {
                        months = 3;
                    } else if (term === 180) {
                        months = 6;
                    } else if (term === 365) {
                        months = 12;
                    }

                    const monthlyInterestRate = annualInterestRate / 12;
                    const applyDate = new Date(loan.apply_date);
                    const plans = [];

                    // 等额本金计算方式
                    if (repayMethod === 'equal-principal') {
                        // 每期应还本金 = 贷款本金÷还款月数
                        const monthlyPrincipal = loanAmount / months;

                        for (let i = 1; i <= months; i++) {
                            // 累计已还本金 = (i-1) × 每期本金
                            const cumulativePrincipal = (i - 1) * monthlyPrincipal;

                            // 每期应还利息 = (贷款本金-累计已还本金)×月利率
                            const interest = (loanAmount - cumulativePrincipal) * monthlyInterestRate;

                            // 当期还款总额 = 月还本金 + 当期利息
                            const amount = monthlyPrincipal + interest;

                            // 计算剩余本金
                            const remainingPrincipal = loanAmount - cumulativePrincipal - monthlyPrincipal;

                            // 计算到期日
                            const dueDate = new Date(applyDate);
                            dueDate.setMonth(dueDate.getMonth() + i);

                            plans.push({
                                period: i,
                                month: i,
                                amount: amount,
                                principal: monthlyPrincipal,
                                interest: interest,
                                dueDate: dueDate.toISOString().split('T')[0],
                                remainingPrincipal: Math.max(0, remainingPrincipal) // 确保不为负数
                            });
                        }
                    }
                    // 等额本息计算方式
                    else {
                        let remainingPrincipal = loanAmount;

                        for (let i = 1; i <= months; i++) {
                            // 计算当期利息
                            const interest = remainingPrincipal * monthlyInterestRate;
                            // 计算当期本金
                            const principal = monthlyPayment - interest;
                            // 更新剩余本金
                            remainingPrincipal -= principal;

                            // 计算到期日
                            const dueDate = new Date(applyDate);
                            dueDate.setMonth(dueDate.getMonth() + i);

                            plans.push({
                                period: i,
                                month: i,
                                amount: monthlyPayment,
                                principal: principal,
                                interest: interest,
                                dueDate: dueDate.toISOString().split('T')[0], // 格式化为YYYY-MM-DD
                                remainingPrincipal: Math.max(0, remainingPrincipal) // 确保不为负数
                            });
                        }
                    }

                    return plans;
                }
            }
            return [];
        });
    }
};

export default {
    user: userApi,
    borrow: borrowApi,
    repay: repayApi
}; 