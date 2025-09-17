<template>
  <view class="container">
    <!-- 头部 -->
    <view class="repay-header">
      <text class="repay-title">待还款总额</text>
      <text class="repay-amount">¥{{formatAmount(totalRepayAmount)}}</text>
    </view>

    <!-- 账单列表 -->
    <view class="bill-list">
      <view class="bill-item" v-for="(item, index) in repayList" :key="index">
        <view class="bill-header">
          <text class="bill-type">贷款编号: {{item.loan_id ? item.loan_id.substring(0, 8) : 'unknown'}}...</text>
          <view :class="['bill-status', getStatusClass(item.daysToExpire || 0)]">
            {{getStatusText(item.daysToExpire || 0)}}
          </view>
        </view>

        <view class="bill-info">
          <view class="bill-amount">
            <text class="info-label">借款金额</text>
            <text class="info-value">¥{{formatAmount(item.loan_amount || 0)}}</text>
          </view>
          <view class="bill-due">
            <text class="info-label">剩余金额</text>
            <text class="info-value">¥{{formatAmount(item.remaining_amount || 0)}}</text>
          </view>
        </view>
        
        <view class="loan-details">
          <view class="detail-row">
            <text class="detail-label">贷款期限</text>
            <text class="detail-value">{{getLoanTermText(item.loan_term || '0')}}</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">还款方式</text>
            <text class="detail-value">{{getRepayMethodText(item.repay_method || 'equal-installment')}}</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">每期还款</text>
            <text class="detail-value">¥{{formatAmount(item.monthly_payment || 0)}}</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">到期日期</text>
            <text class="detail-value">{{item.next_payment_date || '未设置'}}</text>
          </view>
        </view>

        <button class="repay-btn" @click="handleRepay(item)">分期还款</button>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="repayList.length === 0 && !loading">
        <image src="/common/static/empty.png" mode="aspectFit" class="empty-image"></image>
        <text class="empty-text">暂无待还款项目</text>
      </view>
      
      <!-- 加载状态 -->
      <view class="loading-state" v-if="loading">
        <text>正在加载还款信息...</text>
      </view>
    </view>

    <view class="repay-notice" v-if="repayList.length > 0">
      <uni-icons type="info" size="16" color="#FF7E00"></uni-icons>
      <text>支持分期还款，提前还款无任何手续费，可节省后续利息支出。</text>
    </view>
  </view>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { formatAmount } from '@/common/utils';

export default {
  data() {
    return {
      repayList: [], // 还款列表
      loading: false
    };
  },
  computed: {
    // 计算总的待还款金额
    totalRepayAmount() {
      try {
        if (!this.repayList || this.repayList.length === 0) {
          return 0;
        }
      return this.repayList.reduce((total, item) => {
          const amount = parseFloat(item.remaining_amount || 0);
          return total + amount;
      }, 0);
      } catch (error) {
        console.error('计算总还款金额失败:', error);
        return 0;
      }
    }
  },
  onLoad() {
    // 检查登录状态
    const token = uni.getStorageSync('token');
    if (!token) {
      uni.navigateTo({
        url: '/pages/login/login'
      });
      return;
    }
    
    // 获取还款列表
    this.getRepaymentList();
  },
  onShow() {
    // 页面每次显示时刷新数据
    this.getRepaymentList();
  },
  onPullDownRefresh() {
    // 下拉刷新
    this.getRepaymentList(() => {
      uni.stopPullDownRefresh();
    });
  },
  methods: {
    ...mapActions('repay', ['getRepayList']),
    
    // 格式化金额
    formatAmount,
    
    // 获取还款列表
    async getRepaymentList(callback) {
      this.loading = true;
      
      try {
        const token = uni.getStorageSync('token');
        if (!token) {
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          });
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/login/login'
            });
          }, 1500);
          return;
        }
        
        // 获取当前登录用户信息
        const userInfo = uni.getStorageSync('userInfo');
        let username = null;
        
        // 多种方式尝试获取用户名
        if (userInfo) {
          if (typeof userInfo === 'string') {
            try {
              const parsedUserInfo = JSON.parse(userInfo);
              username = parsedUserInfo.username || parsedUserInfo.realName || parsedUserInfo.name;
            } catch (e) {
              username = userInfo; // 如果解析失败，假设userInfo本身就是用户名
            }
          } else if (typeof userInfo === 'object') {
            username = userInfo.username || userInfo.realName || userInfo.name;
          }
        }
        
        // 如果还是没有用户名，提示用户重新登录
        if (!username) {
          console.log('用户信息:', userInfo);
          console.log('Token:', token);
          
          uni.showModal({
            title: '提示',
            content: '用户信息已过期，请重新登录',
            showCancel: false,
            success: () => {
              uni.navigateTo({
                url: '/pages/login/login'
              });
        }
          });
          return;
        }
        
        console.log('使用用户名:', username);
        
        // 直接调用后端API获取用户的贷款数据
        const response = await new Promise((resolve, reject) => {
          console.log(`正在请求API: http://localhost:8000/loan/list?username=${username}`);
          
          uni.request({
            url: `http://localhost:8000/loan/list?username=${username}`,
            method: 'GET',
            header: {
              'Content-Type': 'application/json'
            },
            timeout: 10000, // 10秒超时
            success: (res) => {
              console.log('API响应状态码:', res.statusCode);
              console.log('API响应数据:', res.data);
              
              if (res.statusCode === 200) {
                resolve(res.data);
              } else {
                const errorMsg = res.data?.message || `HTTP错误: ${res.statusCode}`;
                console.error('API返回错误:', errorMsg);
                reject(new Error(errorMsg));
              }
            },
            fail: (err) => {
              console.error('网络请求失败详情:', err);
              // 检查是否是网络连接问题
              if (err.errMsg && err.errMsg.includes('connect fail')) {
                reject(new Error('无法连接到服务器，请确保后端服务已启动'));
              } else {
                reject(new Error('网络请求失败: ' + (err.errMsg || JSON.stringify(err))));
              }
            }
          });
        });
        
        console.log('获取到的贷款数据:', response);
        
        if (response.loans && response.loans.length > 0) {
          console.log('开始过滤贷款数据...');
          
          // 过滤出状态为approved且有剩余金额的贷款（待还款）
          const filteredLoans = response.loans.filter(loan => {
            console.log(`贷款 ${loan.loan_id}: status=${loan.status}, remaining_amount=${loan.remaining_amount}`);
            const isApproved = loan.status === 'approved';
            const hasRemaining = parseFloat(loan.remaining_amount || 0) > 0;
            console.log(`  过滤结果: isApproved=${isApproved}, hasRemaining=${hasRemaining}`);
            return isApproved && hasRemaining;
          });
          
          console.log(`过滤后的贷款数量: ${filteredLoans.length}`);
          
          this.repayList = filteredLoans.map((loan, index) => {
            console.log(`处理第${index + 1}个贷款:`, loan);
            
            // 计算距离到期的天数
            let daysToExpire = 30; // 默认30天
            try {
              if (loan.next_payment_date) {
            const dueDate = new Date(loan.next_payment_date);
            const today = new Date();
            const timeDiff = dueDate.getTime() - today.getTime();
                daysToExpire = Math.ceil(timeDiff / (1000 * 3600 * 24));
                console.log(`  计算到期天数: ${daysToExpire}`);
              }
            } catch (e) {
              console.error('计算到期日期失败:', e);
            }
            
            const processedLoan = {
              ...loan,
              daysToExpire,
              id: loan.loan_id || 'unknown',
              title: `贷款编号: ${loan.loan_id ? loan.loan_id.substring(0, 8) : 'unknown'}...`,
              amount: parseFloat(loan.loan_amount || 0),
              dueDate: loan.next_payment_date || '未设置'
            };
            
            console.log(`  处理后的贷款:`, processedLoan);
            return processedLoan;
          });
          
          console.log(`最终还款列表长度: ${this.repayList.length}`);
        } else {
          console.log('没有贷款数据');
          this.repayList = [];
        }
        
        console.log('处理后的还款列表:', this.repayList);
        
        // 数据加载成功
        if (this.repayList.length > 0) {
          uni.showToast({
            title: `成功加载${this.repayList.length}条还款记录`,
            icon: 'success',
            duration: 2000
          });
        } else {
          uni.showToast({
            title: '暂无待还款项目',
            icon: 'none',
            duration: 2000
          });
        }
        
      } catch (error) {
        console.error('获取还款列表失败', error);
        uni.showToast({
          title: `获取数据失败: ${error.message}`,
          icon: 'none',
          duration: 3000
        });
        this.repayList = [];
      } finally {
        this.loading = false;
        if (callback) callback();
      }
    },
    
    // 获取贷款期限文本
    getLoanTermText(term) {
      const termNum = parseInt(term);
      if (termNum <= 31) {
        return `${termNum}天`;
      } else if (termNum == 90) {
        return '3个月';
      } else if (termNum == 180) {
        return '6个月';
      } else if (termNum == 365) {
        return '12个月';
      } else {
        return `${termNum}个月`;
      }
    },
    
    // 获取还款方式文本
    getRepayMethodText(method) {
      if (method === 'equal-principal') {
        return '等额本金';
      } else if (method === 'equal-installment') {
        return '等额本息';
      } else {
        return '等额本息'; // 默认
      }
    },
    
    // 获取状态类
    getStatusClass(daysToExpire) {
      return daysToExpire <= 7 ? 'urgent' : 'normal';
    },
    
    // 获取状态文本
    getStatusText(daysToExpire) {
      if (daysToExpire < 0) return '已逾期';
      return daysToExpire <= 7 ? `${daysToExpire}天后到期` : `${daysToExpire}天后到期`;
    },
    
    // 处理还款
    handleRepay(item) {
      console.log('点击还款，项目信息:', item);
      
      // 清理项目信息，移除无效字段
      const cleanItem = {
        loan_id: item.loan_id,
        username: item.username,
        loan_amount: item.loan_amount,
        loan_term: item.loan_term,
        interest_rate: item.interest_rate,
        monthly_payment: item.monthly_payment,
        status: item.status,
        apply_date: item.apply_date,
        approve_date: item.approve_date,
        remaining_amount: item.remaining_amount,
        next_payment_date: item.next_payment_date,
        repay_method: item.repay_method || 'equal-installment',
        daysToExpire: item.daysToExpire,
        id: item.id,
        title: item.title,
        amount: item.amount,
        dueDate: item.dueDate
      };
      
      console.log('清理后的项目信息:', cleanItem);
      
      // 存储清理后的还款信息到本地
      uni.setStorageSync('currentRepayItem', JSON.stringify(cleanItem));
      
      // 跳转到还款确认页面
      uni.navigateTo({
        url: `/pages/repay-confirm/repay-confirm?id=${cleanItem.loan_id}&amount=${cleanItem.remaining_amount}&term=${cleanItem.loan_term}&rate=${cleanItem.interest_rate}&method=${cleanItem.repay_method}`
      });
    }
  }
};
</script>

<style lang="scss">
.container {
  padding-bottom: 30rpx;
}

.repay-header {
  background: linear-gradient(135deg, #33B19E, #29A28E);
  color: white;
  padding: 50rpx 30rpx;
  border-radius: 0 0 40rpx 40rpx;
  margin: -1px -1px 40rpx -1px;
  text-align: center;
}

.repay-title {
  font-size: 32rpx;
  opacity: 0.9;
  margin-bottom: 20rpx;
  display: block;
}

.repay-amount {
  font-size: 64rpx;
  font-weight: 600;
  margin-bottom: 10rpx;
  display: block;
}

.bill-list {
  padding: 0 30rpx;
  margin-bottom: 40rpx;
}

.bill-item {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.bill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.bill-type {
  font-size: 32rpx;
  font-weight: 500;
  flex: 1;
}

.bill-status {
  padding: 8rpx 20rpx;
  border-radius: 24rpx;
  font-size: 24rpx;
}

.bill-status.urgent {
  background-color: #FEE5E5;
  color: #FF5151;
}

.bill-status.normal {
  background-color: #E5F7F2;
  color: #33B19E;
}

.bill-info {
  display: flex;
  margin-bottom: 30rpx;
}

.bill-amount {
  flex: 1;
  border-right: 1px solid #eee;
  padding-right: 30rpx;
}

.bill-due {
  flex: 1;
  padding-left: 30rpx;
}

.info-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 10rpx;
  display: block;
}

.info-value {
  font-size: 36rpx;
  font-weight: 500;
  color: #333;
  display: block;
}

.loan-details {
  background-color: #f8f9fa;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 30rpx;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 26rpx;
  color: #666;
}

.detail-value {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.repay-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: 500;
}

.repay-notice {
  background-color: #FFF8E6;
  border-radius: 20rpx;
  padding: 24rpx 30rpx;
  font-size: 26rpx;
  color: #FF7E00;
  margin: 0 30rpx;
  display: flex;
  align-items: flex-start;
}

.repay-notice text {
  margin-left: 16rpx;
  flex: 1;
  line-height: 1.5;
}

.empty-state, .loading-state {
  padding: 100rpx 0;
  text-align: center;
}

.empty-image {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 20rpx;
}

.empty-text, .loading-state text {
  font-size: 28rpx;
  color: #999;
}
</style> 