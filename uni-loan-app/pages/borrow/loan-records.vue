<template>
  <view class="container">
    <!-- 头部 -->
    <view class="history-header">
      <text class="history-title">借款记录</text>
    </view>
    
    <!-- 筛选条件 -->
    <view class="filter-bar">
      <view 
        v-for="(item, index) in filterOptions" 
        :key="index"
        :class="['filter-item', { active: currentFilter === item.value }]"
        @click="changeFilter(item.value)"
      >
        {{item.label}}
      </view>
    </view>
    
    <!-- 记录列表 -->
    <view class="loan-list">
      <view class="loan-item" v-for="(item, index) in filteredRecords" :key="index">
        <view class="item-header">
          <text class="item-title">贷款借款</text>
          <view :class="['item-status', getStatusClass(item.status)]">
            {{getStatusText(item.status)}}
          </view>
        </view>
        
        <view class="item-info">
          <view class="info-row">
            <text class="info-label">借款金额</text>
            <text class="info-value">¥{{formatAmount(item.amount)}}</text>
          </view>
          <view class="info-row">
            <text class="info-label">借款期限</text>
            <text class="info-value">{{formatLoanTerm(item.term)}}</text>
          </view>
          <view class="info-row">
            <text class="info-label">借款日期</text>
            <text class="info-value">{{item.applyDate}}</text>
          </view>
          <view class="info-row">
            <text class="info-label">到期日</text>
            <text class="info-value">{{item.dueDate}}</text>
          </view>
          <view class="info-row">
            <text class="info-label">剩余未还</text>
            <text class="info-value">¥{{formatAmount(item.remainingAmount)}}</text>
          </view>
          <view class="info-row">
            <text class="info-label">月供金额</text>
            <text class="info-value">{{formatMonthlyPayment(item)}}</text>
          </view>
        </view>
        
        <view class="item-buttons" v-if="item.status === 'approved' && item.remainingAmount > 0">
          <button class="repay-btn" @click="goToRepay(item)">去还款</button>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-if="filteredRecords.length === 0">
        <image src="/common/static/empty.png" mode="aspectFit" class="empty-image"></image>
        <text class="empty-text">暂无{{getEmptyText()}}借款记录</text>
      </view>
    </view>
  </view>
</template>

<script>
import { formatAmount } from '@/common/utils';
import { mapState, mapActions } from 'vuex';

export default {
  data() {
    return {
      filterOptions: [
        { label: '全部', value: 'all' },
        { label: '还款中', value: 'approved' },
        { label: '已还清', value: 'completed' }
      ],
      currentFilter: 'all'
    };
  },
  computed: {
    ...mapState('loan', ['loanRecords']),
    // 根据筛选条件过滤记录
    filteredRecords() {
      let records = [];
      
      if (this.currentFilter === 'all') {
        records = [...this.loanRecords];
      } else {
        records = this.loanRecords.filter(item => item.status === this.currentFilter);
      }
      
      // 对记录进行排序：还款中的记录（未还款）排在前面，已还清的排在后面
      return records.sort((a, b) => {
        if (a.status === 'completed' && a.remainingAmount <= 0 && 
            (b.status === 'approved' || b.remainingAmount > 0)) {
          return 1; // a是已还清记录，b是未还清，a排后面
        } else if ((a.status === 'approved' || a.remainingAmount > 0) && 
                   b.status === 'completed' && b.remainingAmount <= 0) {
          return -1; // a是未还清记录，b是已还清，a排前面
        } else {
          return 0; // 保持原顺序
        }
      });
    }
  },
  onLoad() {
    // 获取借款记录
    this.getLoanRecordsList();
  },
  onPullDownRefresh() {
    // 下拉刷新
    this.getLoanRecordsList(() => {
      uni.stopPullDownRefresh();
    });
  },
  methods: {
    ...mapActions('loan', {
      fetchLoanRecords: 'getLoanRecords'
    }),
    // 格式化金额
    formatAmount,
    
    // 格式化月供金额
    formatMonthlyPayment(item) {
      if (item.term <= 31) { // 短期贷款
        return '一次性还款';
      }
      return `¥${this.formatAmount(item.monthlyPayment)}`;
    },
    
    // 格式化借款期限
    formatLoanTerm(term) {
      // 根据term值确定是天数还是月数
      const termInt = parseInt(term);
      if (termInt <= 31) {
        return `${termInt}天`;
      } else if (termInt === 90) {
        return '3个月';
      } else if (termInt === 180) {
        return '6个月';
      } else if (termInt === 365) {
        return '12个月';
      } else {
        // 如果不是上述特殊值，按月份计算（term可能是月数）
        return `${termInt}个月`;
      }
    },
    
    // 更改筛选条件
    changeFilter(value) {
      this.currentFilter = value;
    },
    
    // 获取状态样式类
    getStatusClass(status) {
      if (status === 'approved') return 'ongoing';
      if (status === 'completed') return 'completed';
      return '';
    },
    
    // 获取状态文本
    getStatusText(status) {
      if (status === 'approved') return '还款中';
      if (status === 'completed') return '已还清';
      if (status === 'pending') return '待审核';
      if (status === 'rejected') return '已拒绝';
      return '未知状态';
    },
    
    // 获取空状态文本
    getEmptyText() {
      if (this.currentFilter === 'approved') return '还款中';
      if (this.currentFilter === 'completed') return '已还清';
      return '';
    },
    
    // 获取借款记录
    getLoanRecordsList(callback) {
      uni.showLoading({
        title: '加载中...'
      });
      
      // 调用store的方法从后端获取数据
      this.fetchLoanRecords()
        .then(() => {
          uni.hideLoading();
          if (callback) callback();
        })
        .catch(err => {
          console.error('获取借款记录失败', err);
          uni.hideLoading();
          if (callback) callback();
        });
    },
    
    // 跳转到还款页面
    goToRepay(item) {
      // 先将当前还款项信息保存到本地存储
      const repayItem = {
        id: item.id,
        title: '贷款还款',
        amount: item.remainingAmount,
        dueDate: item.dueDate,
        daysToExpire: this.calculateDaysToExpire(item.dueDate),
        monthlyPayment: item.monthlyPayment
      };
      
      uni.setStorageSync('currentRepayItem', JSON.stringify(repayItem));
      
      // 跳转到还款页面，并传递贷款ID和金额
      uni.navigateTo({
        url: `/pages/repay-confirm/repay-confirm?id=${item.id}&amount=${item.remainingAmount}`
      });
    },
    
    // 计算距离到期日的天数
    calculateDaysToExpire(dueDate) {
      if (!dueDate) return 30; // 默认30天
      
      const today = new Date();
      const dueDateObj = new Date(dueDate);
      const diffTime = dueDateObj - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      return diffDays > 0 ? diffDays : 0;
    }
  }
};
</script>

<style lang="scss">
.container {
  padding-bottom: 30rpx;
}

.history-header {
  background: linear-gradient(135deg, #FF7E00, #FF5500);
  color: white;
  padding: 50rpx 30rpx;
  border-radius: 0 0 40rpx 40rpx;
  margin: -1px -1px 40rpx -1px;
  text-align: center;
}

.history-title {
  font-size: 36rpx;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  justify-content: space-around;
  background-color: white;
  margin: 0 30rpx 30rpx;
  border-radius: 30rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.filter-item {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  font-size: 28rpx;
  color: #666;
  position: relative;
}

.filter-item.active {
  color: #FF7E00;
  font-weight: 500;
}

.filter-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 6rpx;
  background-color: #FF7E00;
  border-radius: 3rpx;
}

.loan-list {
  padding: 0 30rpx;
}

.loan-item {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #f5f5f5;
}

.item-title {
  font-size: 32rpx;
  font-weight: 500;
}

.item-status {
  padding: 8rpx 20rpx;
  border-radius: 24rpx;
  font-size: 24rpx;
}

.item-status.ongoing {
  background-color: #FFF8E6;
  color: #FF7E00;
}

.item-status.completed {
  background-color: #E5F7F2;
  color: #33B19E;
}

.item-info {
  padding-top: 10rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 28rpx;
  color: #666;
}

.info-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.item-buttons {
  margin-top: 30rpx;
  display: flex;
  justify-content: flex-end;
}

.repay-btn {
  background: linear-gradient(to right, #FF7E00, #FF5500);
  color: white;
  font-size: 28rpx;
  padding: 10rpx 40rpx;
  border-radius: 30rpx;
  border: none;
}

.empty-state {
  padding: 100rpx 0;
  text-align: center;
}

.empty-image {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}
</style> 