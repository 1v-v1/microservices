<template>
  <view class="container">
    <view class="success-icon">
      <image src="/common/static/success.png" mode="aspectFit"></image>
    </view>
    
    <view class="success-text">
      <text class="success-title">还款成功</text>
      <text class="success-amount">￥{{formatAmount(repayAmount)}}</text>
      <text class="success-desc" v-if="periods === 1">您的一次性还款已成功处理</text>
      <text class="success-desc" v-else>您的第1期还款已成功处理</text>
    </view>
    
    <!-- 还款信息 -->
    <view class="repay-info">
      <view class="info-title">还款详情</view>
      <view class="info-row">
        <text class="info-label">本次还款金额</text>
        <text class="info-value">￥{{formatAmount(repayAmount)}}</text>
      </view>
      <view class="info-row" v-if="remainingAmount > 0">
        <text class="info-label">剩余待还金额</text>
        <text class="info-value">￥{{formatAmount(remainingAmount)}}</text>
      </view>
      <view class="info-row" v-else>
        <text class="info-label">还款状态</text>
        <text class="info-value success-status">已全部还清</text>
      </view>
      <view class="info-row" v-if="periods > 1">
        <text class="info-label">还款期数</text>
        <text class="info-value">第1期/共{{periods}}期</text>
      </view>
    </view>
    
    <view class="success-tips">
      <view class="tip-item">
        <uni-icons type="info" size="16" color="#33B19E"></uni-icons>
        <text>还款信息将在1-2个工作日内更新</text>
      </view>
      <view class="tip-item" v-if="periods > 1">
        <uni-icons type="info" size="16" color="#33B19E"></uni-icons>
        <text>下期还款将在约定时间自动提醒</text>
      </view>
      <view class="tip-item">
        <uni-icons type="info" size="16" color="#33B19E"></uni-icons>
        <text>您可以在"我的借款"中查看最新的还款记录</text>
      </view>
    </view>
    
    <view class="button-group">
      <button class="btn primary-btn" @click="goToRepayHistory">查看还款记录</button>
      <button class="btn secondary-btn" @click="goToHome">返回首页</button>
    </view>
  </view>
</template>

<script>
import { formatAmount } from '@/common/utils';

export default {
  data() {
    return {
      repayAmount: 0,
      periods: 1,
      remainingAmount: 0
    };
  },
  onLoad(options) {
    // 获取路由参数中的还款金额和期数
    if (options.amount) {
      this.repayAmount = parseFloat(options.amount);
    }
    if (options.periods) {
      this.periods = parseInt(options.periods);
    }
    if (options.remainingAmount) {
      this.remainingAmount = parseFloat(options.remainingAmount);
    }
    
    console.log('还款成功页面参数:', { 
      amount: this.repayAmount, 
      periods: this.periods, 
      remainingAmount: this.remainingAmount 
    });
    
    // 通知后端更新用户信息（如有需要）
    this.updateUserInfo();
  },
  methods: {
    // 格式化金额
    formatAmount,
    
    // 更新用户信息
    updateUserInfo() {
      // 可以在这里调用接口更新用户的最新信息
      // 例如借款状态、信用分等
    },
    
    // 跳转到还款记录页面
    goToRepayHistory() {
      uni.redirectTo({
        url: '/pages/repay-history/repay-history'
      });
    },
    
    // 返回首页
    goToHome() {
      uni.switchTab({
        url: '/pages/index/index'
      });
    }
  }
};
</script>

<style lang="scss">
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 40rpx;
  background-color: #fff;
  min-height: 100vh;
}

.success-icon {
  margin: 60rpx 0;
  
  image {
    width: 160rpx;
    height: 160rpx;
  }
}

.success-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40rpx;
}

.success-title {
  font-size: 40rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 30rpx;
}

.success-amount {
  font-size: 64rpx;
  font-weight: 600;
  color: #33B19E;
  margin-bottom: 20rpx;
}

.success-desc {
  font-size: 28rpx;
  color: #666;
}

.repay-info {
  width: 100%;
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.info-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
  text-align: center;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
  padding: 8rpx 0;
}

.info-row:last-child {
  margin-bottom: 0;
  border-top: 1px solid #f0f0f0;
  padding-top: 16rpx;
  margin-top: 8rpx;
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

.success-status {
  color: #33B19E;
  font-weight: 600;
}

.success-tips {
  width: 100%;
  background-color: #f8f8f8;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 80rpx;
}

.tip-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  text {
    font-size: 26rpx;
    color: #666;
    margin-left: 10rpx;
    line-height: 1.4;
  }
}

.button-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-top: 40rpx;
}

.btn {
  width: 100%;
  height: 90rpx;
  border-radius: 45rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 500;
  margin-bottom: 30rpx;
}

.primary-btn {
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
}

.secondary-btn {
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
}
</style> 