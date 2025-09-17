<template>
  <view class="container">
    <!-- 头部 -->
    <view class="history-header">
      <text class="history-title">还款记录</text>
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
    <view class="history-list">
      <view class="history-item" v-for="(item, index) in filteredRecords" :key="index">
        <view class="item-header">
          <text class="item-title">贷款还款</text>
          <view :class="['item-status', getStatusClass(item.status)]">
            {{getStatusText(item.status)}}
          </view>
        </view>
        
        <view class="item-info">
          <view class="info-row">
            <text class="info-label">还款金额</text>
            <text class="info-value">¥{{formatAmount(item.amount)}}</text>
          </view>
          <view class="info-row">
            <text class="info-label">还款时间</text>
            <text class="info-value">{{item.paymentDate || '-'}}</text>
          </view>
          <view class="info-row" v-if="item.periods && item.periods > 1">
            <text class="info-label">还款期数</text>
            <text class="info-value">{{item.periods}}期</text>
          </view>
          <view class="info-row">
            <text class="info-label">支付方式</text>
            <text class="info-value">{{getPaymentMethodText(item.payment_method)}}</text>
          </view>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-if="filteredRecords.length === 0">
        <image src="/common/static/empty.png" mode="aspectFit" class="empty-image"></image>
        <text class="empty-text">暂无{{getEmptyText()}}还款记录</text>
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
        { label: '已还清', value: 'completed' },
        { label: '已逾期', value: 'overdue' }
      ],
      currentFilter: 'all',
      repayHistoryList: []
    };
  },
  computed: {
    ...mapState('repay', ['repaymentHistory']),
    // 根据筛选条件过滤记录
    filteredRecords() {
      let records = [];
      if (this.currentFilter === 'all') {
        records = [...this.repaymentHistory];
      } else {
        records = this.repaymentHistory.filter(item => item.status === this.currentFilter);
      }
      
      // 对记录进行排序：待还款和逾期记录排在前面，已还清记录排在后面
      return records.sort((a, b) => {
        if (a.status === 'completed' && (b.status === 'pending' || b.status === 'overdue')) {
          return 1; // a是已还清记录，b是待还款或逾期，a排后面
        } else if ((a.status === 'pending' || a.status === 'overdue') && b.status === 'completed') {
          return -1; // a是待还款或逾期，b是已还清，a排前面
        } else {
          return 0; // 保持原顺序
        }
      });
    }
  },
  onLoad() {
    // 获取还款记录
    this.getRepaymentHistory();
  },
  onPullDownRefresh() {
    // 下拉刷新
    this.getRepaymentHistory(() => {
      uni.stopPullDownRefresh();
    });
  },
  methods: {
    ...mapActions('repay', {
      fetchRepaymentHistory: 'getRepaymentHistory'
    }),
    // 格式化金额
    formatAmount,
    
    // 更改筛选条件
    changeFilter(value) {
      this.currentFilter = value;
    },
    
    // 获取状态样式类
    getStatusClass(status) {
      if (status === 'overdue') return 'overdue';
      if (status === 'completed') return 'paid';
      return '';
    },
    
    // 获取状态文本
    getStatusText(status) {
      if (status === 'completed') return '已还清';
      if (status === 'overdue') return '已逾期';
      if (status === 'pending') return '待还款';
      return '待还款';
    },
    
    // 获取空状态文本
    getEmptyText() {
      if (this.currentFilter === 'completed') return '已还清';
      if (this.currentFilter === 'overdue') return '逾期';
      return '';
    },
    
    // 获取支付方式文本
    getPaymentMethodText(method) {
      if (method === 'alipay') return '支付宝';
      if (method === 'wechat') return '微信支付';
      if (method === 'bank') return '银行卡';
      return '系统还款';
    },
    
    // 获取还款记录
    getRepaymentHistory(callback) {
      uni.showLoading({
        title: '加载中...'
      });
      
      // 调用store的方法从后端获取数据
      this.fetchRepaymentHistory()
        .then(() => {
          uni.hideLoading();
          if (callback) callback();
        })
        .catch(err => {
          console.error('获取还款记录失败', err);
          uni.hideLoading();
          if (callback) callback();
        });
    }
  }
};
</script>

<style lang="scss">
.container {
  padding-bottom: 30rpx;
}

.history-header {
  background: linear-gradient(135deg, #33B19E, #29A28E);
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
  color: #33B19E;
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
  background-color: #33B19E;
  border-radius: 3rpx;
}

.history-list {
  padding: 0 30rpx;
}

.history-item {
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

.item-status.overdue {
  background-color: #FEE5E5;
  color: #FF5151;
}

.item-status.paid {
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