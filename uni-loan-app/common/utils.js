// 通用工具函数

/**
 * 格式化金额，添加千分位分隔符
 * @param {Number} amount - 金额数值
 * @param {Number} decimals - 小数位数
 * @returns {String} 格式化后的金额字符串
 */
export const formatAmount = (amount, decimals = 2) => {
    if (isNaN(amount) || amount === null) return '0.00';

    const num = parseFloat(amount).toFixed(decimals);

    // 添加千分位分隔符
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

/**
 * 格式化日期
 * @param {Date|String|Number} date - 日期对象、字符串或时间戳
 * @param {String} format - 格式化模板，如 'YYYY-MM-DD'
 * @returns {String} 格式化后的日期字符串
 */
export const formatDate = (date, format = 'YYYY-MM-DD') => {
    if (!date) return '';

    const d = new Date(date);

    const year = d.getFullYear();
    const month = d.getMonth() + 1;
    const day = d.getDate();
    const hour = d.getHours();
    const minute = d.getMinutes();
    const second = d.getSeconds();

    // 补零函数
    const pad = (n) => n < 10 ? '0' + n : n;

    return format
        .replace('YYYY', year)
        .replace('MM', pad(month))
        .replace('DD', pad(day))
        .replace('HH', pad(hour))
        .replace('mm', pad(minute))
        .replace('ss', pad(second));
};

/**
 * 计算还款计划 - 等额本金
 * @param {Number} principal - 借款本金
 * @param {Number} months - 借款期限(月)
 * @param {Number} annualRate - 年化利率(小数)
 * @returns {Object} 还款计划对象
 */
export const calculateEqualPrincipal = (principal, months, annualRate) => {
    const monthlyRate = annualRate / 12; // 月利率
    const monthlyPrincipal = principal / months; // 每期应还本金 = 贷款本金÷还款月数
    const plan = [];

    // 使用公式计算总利息：还款总利息 = (还款月数+1)×贷款本金×月利率÷2
    const totalInterest = (months + 1) * principal * monthlyRate / 2;

    let totalPrincipal = 0;
    let calculatedTotalInterest = 0; // 用于累计实际计算的利息

    for (let i = 1; i <= months; i++) {
        // 累计已还本金 = (i-1) × 每期本金
        const cumulativePrincipal = (i - 1) * monthlyPrincipal;

        // 每期应还利息 = (贷款本金-累计已还本金)×月利率
        const interest = (principal - cumulativePrincipal) * monthlyRate;

        // 最后一个月调整本金，确保总额准确
        let actualPrincipal = monthlyPrincipal;
        if (i === months) {
            actualPrincipal = principal - totalPrincipal;
        }

        // 每期应还总额 = 每期应还本金+每期应还利息
        const payment = actualPrincipal + interest;

        totalPrincipal += actualPrincipal;
        calculatedTotalInterest += interest;

        // 计算还款日期
        const today = new Date();
        const paymentDate = new Date(today);
        paymentDate.setMonth(today.getMonth() + i);

        // 计算剩余本金
        const remainingPrincipal = principal - cumulativePrincipal - actualPrincipal;

        plan.push({
            month: i,
            paymentDate: formatDate(paymentDate),
            payment: payment.toFixed(2),
            principal: actualPrincipal.toFixed(2),
            interest: interest.toFixed(2),
            remainingPrincipal: Math.max(0, remainingPrincipal).toFixed(2)
        });
    }

    return {
        plan,
        totalPayment: (totalPrincipal + totalInterest).toFixed(2), // 使用公式计算的总利息
        totalPrincipal: totalPrincipal.toFixed(2),
        totalInterest: totalInterest.toFixed(2) // 使用公式计算的总利息
    };
};

/**
 * 计算还款计划 - 等额本息
 * @param {Number} principal - 借款本金
 * @param {Number} months - 借款期限(月)
 * @param {Number} annualRate - 年化利率(小数)
 * @returns {Array} 还款计划数组
 */
export const calculateEqualInstallment = (principal, months, annualRate) => {
    const monthlyRate = annualRate / 12;
    const monthlyPayment = (principal * monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);

    const plan = [];
    let remainingPrincipal = principal;
    let totalPrincipal = 0;
    let totalInterest = 0;

    for (let i = 1; i <= months; i++) {
        const interest = remainingPrincipal * monthlyRate;
        let currentPrincipal = monthlyPayment - interest;

        // 最后一个月调整本金，确保总额准确
        if (i === months) {
            currentPrincipal = remainingPrincipal;
        }

        const payment = currentPrincipal + interest;

        remainingPrincipal -= currentPrincipal;
        totalPrincipal += currentPrincipal;
        totalInterest += interest;

        // 计算还款日期
        const today = new Date();
        const paymentDate = new Date(today);
        paymentDate.setMonth(today.getMonth() + i);

        plan.push({
            month: i,
            paymentDate: formatDate(paymentDate),
            payment: payment.toFixed(2),
            principal: currentPrincipal.toFixed(2),
            interest: interest.toFixed(2),
            remainingPrincipal: remainingPrincipal.toFixed(2)
        });
    }

    return {
        plan,
        totalPayment: (totalPrincipal + totalInterest).toFixed(2),
        totalPrincipal: totalPrincipal.toFixed(2),
        totalInterest: totalInterest.toFixed(2)
    };
};

/**
 * 解析URL参数
 * @param {String} url - URL字符串
 * @returns {Object} 参数对象
 */
export const parseUrlParams = (url) => {
    const params = {};
    const query = url.split('?')[1];

    if (!query) return params;

    const pairs = query.split('&');

    for (let i = 0; i < pairs.length; i++) {
        const pair = pairs[i].split('=');
        params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }

    return params;
};

/**
 * 本地存储封装
 */
export const storage = {
    set(key, value) {
        try {
            uni.setStorageSync(key, JSON.stringify(value));
        } catch (e) {
            console.error('存储数据失败', e);
        }
    },

    get(key) {
        try {
            const value = uni.getStorageSync(key);
            return value ? JSON.parse(value) : null;
        } catch (e) {
            console.error('获取数据失败', e);
            return null;
        }
    },

    remove(key) {
        try {
            uni.removeStorageSync(key);
        } catch (e) {
            console.error('删除数据失败', e);
        }
    },

    clear() {
        try {
            uni.clearStorageSync();
        } catch (e) {
            console.error('清空数据失败', e);
        }
    }
}; 