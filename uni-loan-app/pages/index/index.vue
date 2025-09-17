<template>
  <view class="container">
    <!-- 头部 -->
    <view class="home-header">
      <view class="home-user">
        <view class="user-avatar">
          <uni-icons type="person" size="22" color="#ffffff"></uni-icons>
        </view>
        <view class="user-info">
          <text class="user-name">{{userInfo.name || '用户'}}</text>
          <view class="credit-display">
            <text class="user-credit">信用分: {{userInfo.creditScore || 700}}</text>
            <view :class="['credit-badge', getCreditLevelClass(userInfo.creditScore)]">
              {{getCreditLevel(userInfo.creditScore)}}
            </view>
          </view>
        </view>
      </view>
      
      <!-- 信用分详细信息卡片 -->
      <view class="credit-summary" @click="viewCreditDetail">
        <view class="credit-summary-item">
          <text class="summary-label">当前信用分</text>
          <text class="summary-value">{{userInfo.creditScore || 700}}分</text>
        </view>
        <view class="credit-summary-item">
          <text class="summary-label">信用等级</text>
          <text class="summary-value">{{getCreditLevel(userInfo.creditScore)}}</text>
        </view>
        <view class="credit-summary-item">
          <text class="summary-label">距离下级</text>
          <text class="summary-value">{{getNextLevelGap(userInfo.creditScore)}}分</text>
        </view>
        <view class="credit-arrow">
          <uni-icons type="right" size="16" color="rgba(255,255,255,0.7)"></uni-icons>
        </view>
      </view>
    </view>

    <!-- 信用卡片 -->
    <view class="credit-card">
      <text class="credit-title">我的借款额度</text>
      <text class="credit-amount">¥{{formatAmount(loanLimit.total)}}</text>

      <view class="credit-progress">
        <view class="progress-circle">
          <view class="progress-canvas">
            <canvas canvas-id="progressCanvas" class="canvas"></canvas>
          </view>
          <text class="progress-text">{{creditPercent}}%</text>
        </view>

        <view class="credit-info">
          <view class="info-item">
            <text>已使用额度</text>
            <text>¥{{formatAmount(loanLimit.used)}}</text>
          </view>
          <view class="info-item">
            <text>可用额度</text>
            <text>¥{{formatAmount(loanLimit.available)}}</text>
          </view>
        </view>
      </view>

      <view class="btn-group">
      <button class="borrow-btn" @click="navigateToBorrow">立即借钱</button>
        <button class="limit-btn" @click="upgradeLimit">提升额度</button>
      </view>
    </view>

    <!-- 借还记录 -->
    <view class="home-section">
      <view class="section-title">
        <text>借还记录</text>
        <navigator url="/pages/record/record" class="section-more">查看全部 <uni-icons type="right" size="14" color="#999"></uni-icons></navigator>
      </view>

      <view class="record-list">
        <view class="record-item" v-for="(item, index) in loanRecords" :key="index">
          <view class="record-info">
            <text class="record-title">{{item.title}}</text>
            <text class="record-date">到期日: {{item.dueDate}}</text>
          </view>
          <view>
            <text class="record-amount">¥{{formatAmount(item.amount)}}</text>
            <view :class="['record-status', getStatusClass(item.status)]">{{getStatusText(item.status)}}</view>
          </view>
        </view>
        
        <view class="empty-records" v-if="loanRecords.length === 0">
          <text class="empty-text">暂无借款记录</text>
        </view>
      </view>
    </view>

    <!-- 轮播广告 -->
    <view class="banner">
      <image src="/common/static/banner.png" class="banner-img" mode="aspectFill"></image>
    </view>

    <!-- 常用功能 -->
    <view class="home-section">
      <view class="section-title">常用功能</view>

      <view class="guide-list">
        <view class="guide-item" @click="navigateToGuide('guide')">
          <view class="guide-icon guide-icon-guide">
            <uni-icons type="help" size="24" color="#FFFFFF"></uni-icons>
          </view>
          <text class="guide-title">新手指南</text>
          <text class="guide-desc">轻松上手借贷流程</text>
        </view>

        <view class="guide-item" @click="navigateToGuide('safety')">
          <view class="guide-icon guide-icon-safety">
            <uni-icons type="locked" size="24" color="#FFFFFF"></uni-icons>
          </view>
          <text class="guide-title">安全中心</text>
          <text class="guide-desc">保障账户交易安全</text>
        </view>

        <view class="guide-item" @click="navigateToGuide('faq')">
          <view class="guide-icon guide-icon-faq">
            <uni-icons type="info" size="24" color="#FFFFFF"></uni-icons>
          </view>
          <text class="guide-title">常见问题</text>
          <text class="guide-desc">解答借贷过程疑惑</text>
        </view>

        <view class="guide-item" @click="navigateToGuide('service')">
          <view class="guide-icon guide-icon-service">
            <uni-icons type="headphones" size="24" color="#FFFFFF"></uni-icons>
          </view>
          <text class="guide-title">在线客服</text>
          <text class="guide-desc">专业顾问实时解答</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { formatAmount } from '@/common/utils';

export default {
  data() {
    return {
      creditPercent: 30, // 信用使用百分比
      loanRecords: [] // 借款记录
    };
  },
  computed: {
    ...mapState('user', ['userInfo']),
    ...mapState('loan', ['loanLimit'])
  },
  onLoad() {
    // 检查登录状态
    if (!this.userInfo) {
      uni.navigateTo({
        url: '/pages/login/login'
      });
      return;
    }
    
    // 获取数据
    this.getLoanData();
  },
  onShow() {
    // 页面显示时更新状态
    if (this.userInfo) {
      this.getLoanData();
    }
  },
  onReady() {
    // canvas绘制完成后开始绘制进度环
    setTimeout(() => {
      this.drawProgressCircle();
    }, 300);
  },
  methods: {
    ...mapActions('loan', ['getLoanLimit', 'getLoanRecords']),
    
    // 格式化金额
    formatAmount,
    
    // 获取贷款数据
    getLoanData() {
      uni.showLoading({
        title: '加载中...'
      });
      
      // 获取借款额度
      this.getLoanLimit()
        .then(() => {
          // 计算额度使用百分比
          if (this.loanLimit.total > 0) {
            this.creditPercent = Math.round((this.loanLimit.used / this.loanLimit.total) * 100);
          }
          this.drawProgressCircle();
        })
        .catch(err => {
          console.error('获取借款额度失败', err);
        });
      
      // 获取借款记录
      this.getLoanRecords()
        .then(res => {
          uni.hideLoading();
          
          if (res && res.length > 0) {
            // 使用API返回的记录
            this.loanRecords = res.map(loan => ({
              title: loan.title || '借款',
              dueDate: loan.dueDate || '未设置',
              amount: loan.amount,
              status: this.mapLoanStatus(loan.status)
            }))
            // 对记录进行排序：未还款（pending）和逾期（overdue）记录排在前面，已还清（paid）记录排在后面
            .sort((a, b) => {
              if (a.status === 'paid' && b.status !== 'paid') {
                return 1; // a是已还清记录，b不是，a排后面
              } else if (a.status !== 'paid' && b.status === 'paid') {
                return -1; // a不是已还清记录，b是，a排前面
              } else {
                return 0; // 保持原顺序
              }
            });
          } else {
            // 如果没有记录，清空列表
            this.loanRecords = [];
          }
        })
        .catch(err => {
          console.error('获取借款记录失败', err);
          uni.hideLoading();
          this.loanRecords = [];
        });
    },
    
    // 映射贷款状态
    mapLoanStatus(status) {
      switch(status) {
        case 'approved': return 'pending';
        case 'completed': return 'paid';
        case 'overdue': return 'overdue';
        default: return 'pending';
      }
    },
    
    // 绘制进度环
    drawProgressCircle() {
      const ctx = uni.createCanvasContext('progressCanvas', this);
      const canvasSize = 80;
      const centerX = canvasSize / 2;
      const centerY = canvasSize / 2;
      const radius = 34;
      
      // 计算百分比对应的角度
      const percent = this.creditPercent || 0;
      const endAngle = (percent / 100) * 2 * Math.PI - 0.5 * Math.PI;
      
      // 绘制背景圆环
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.setStrokeStyle('#f1f1f1');
      ctx.setLineWidth(4);
      ctx.stroke();
      
      // 绘制进度圆环
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, -0.5 * Math.PI, endAngle);
      ctx.setStrokeStyle('#33B19E');
      ctx.setLineWidth(4);
      ctx.stroke();
      
      ctx.draw();
    },
    
    // 获取状态类
    getStatusClass(status) {
      if (status === 'overdue') return 'overdue';
      if (status === 'paid') return 'paid';
      return '';
    },
    
    // 获取状态文本
    getStatusText(status) {
      if (status === 'pending') return '待还款';
      if (status === 'overdue') return '已逾期';
      if (status === 'paid') return '已还清';
      return '待还款';
    },
    
    // 跳转到借款页面
    navigateToBorrow() {
      uni.switchTab({
        url: '/pages/borrow/borrow'
      });
    },
    
    // 跳转到指南页面
    navigateToGuide(type) {
      uni.navigateTo({
        url: `/pages/guide/guide?type=${type}`
      });
    },
    
    // 提升额度
    upgradeLimit() {
      uni.navigateTo({
        url: '/pages/user-info/user-info'
      });
    },
    
    // 信用分相关方法
    getCreditLevel(score) {
      const numScore = parseInt(score) || 700;
      if (numScore >= 700) return '优秀';
      if (numScore >= 650) return '良好';
      if (numScore >= 600) return '中等';
      if (numScore >= 550) return '及格';
      return '较差';
    },
    
    getCreditLevelClass(score) {
      const numScore = parseInt(score) || 700;
      if (numScore >= 700) return 'excellent';
      if (numScore >= 650) return 'good';
      if (numScore >= 600) return 'fair';
      if (numScore >= 550) return 'pass';
      return 'poor';
    },
    
    getNextLevelGap(score) {
      const numScore = parseInt(score) || 700;
      if (numScore >= 700) return '已达最高';
      if (numScore >= 650) return 700 - numScore;
      if (numScore >= 600) return 650 - numScore;
      if (numScore >= 550) return 600 - numScore;
      return 550 - numScore;
    },
    
    // 查看信用分详情
    viewCreditDetail() {
      uni.showModal({
        title: '信用分详情',
        content: `当前信用分: ${this.userInfo.creditScore || 700}分\n信用等级: ${this.getCreditLevel(this.userInfo.creditScore)}\n\n完善个人信息可以提升信用分，获得更高贷款额度。`,
        showCancel: true,
        cancelText: '取消',
        confirmText: '完善信息',
        success: (res) => {
          if (res.confirm) {
            this.upgradeLimit();
          }
        }
      });
    }
  }
};
</script>

<style lang="scss">
.container {
  padding-bottom: 120rpx;
}

.home-header {
  background: linear-gradient(135deg, #33B19E, #29A28E);
  color: white;
  padding: 40rpx 30rpx;
  border-radius: 0 0 40rpx 40rpx;
  margin: -1px -1px 40rpx -1px;
}

.home-user {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.user-name {
  font-size: 36rpx;
  font-weight: 500;
  display: block;
}

.user-info {
  flex: 1;
}

.credit-display {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 8rpx;
}

.user-credit {
  font-size: 26rpx;
  opacity: 0.8;
}

.credit-badge {
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 500;
  color: white;
}

.credit-badge.excellent {
  background-color: rgba(103, 194, 58, 0.9);
}

.credit-badge.good {
  background-color: rgba(64, 158, 255, 0.9);
}

.credit-badge.fair {
  background-color: rgba(230, 162, 60, 0.9);
}

.credit-badge.pass {
  background-color: rgba(144, 147, 153, 0.9);
}

.credit-badge.poor {
  background-color: rgba(245, 108, 108, 0.9);
}

.credit-summary {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-top: 30rpx;
  display: flex;
  align-items: center;
  position: relative;
}

.credit-summary-item {
  flex: 1;
  text-align: center;
}

.summary-label {
  font-size: 24rpx;
  opacity: 0.7;
  display: block;
  margin-bottom: 8rpx;
}

.summary-value {
  font-size: 28rpx;
  font-weight: 500;
  display: block;
}

.credit-arrow {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
}

.credit-card {
  background-color: white;
  border-radius: 20rpx;
  padding: 40rpx;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  margin: 0 30rpx;
}

.credit-card::before {
  content: "";
  position: absolute;
  top: -100rpx;
  right: -100rpx;
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  background-color: rgba(51, 177, 158, 0.1);
}

.credit-title {
  color: #666;
  font-size: 28rpx;
  margin-bottom: 20rpx;
  display: block;
}

.credit-amount {
  font-size: 72rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 40rpx;
  display: block;
}

.credit-progress {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.progress-circle {
  width: 160rpx;
  height: 160rpx;
  position: relative;
}

.progress-canvas {
  width: 160rpx;
  height: 160rpx;
}

.canvas {
  width: 160rpx;
  height: 160rpx;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 28rpx;
  font-weight: 500;
  color: #33B19E;
}

.credit-info {
  flex: 1;
  padding-left: 30rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 28rpx;
  margin-bottom: 16rpx;
  color: #666;
}

.btn-group {
  display: flex;
  justify-content: space-between;
  margin-top: 40rpx;
}

.borrow-btn {
  display: block;
  width: 48%;
  height: 100rpx;
  background: linear-gradient(to right, #FF7E00, #FF5500);
  color: white;
  border: none;
  border-radius: 20rpx;
  font-size: 32rpx;
  font-weight: 500;
  box-shadow: 0 10rpx 20rpx rgba(255, 126, 0, 0.3);
}

.limit-btn {
  display: block;
  width: 48%;
  height: 100rpx;
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
  border-radius: 20rpx;
  font-size: 32rpx;
  font-weight: 500;
  box-shadow: 0 10rpx 20rpx rgba(51, 177, 158, 0.3);
}

.home-section {
  margin: 50rpx 30rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: 500;
  margin-bottom: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-more {
  font-size: 28rpx;
  color: #999;
  font-weight: normal;
  display: flex;
  align-items: center;
}

.record-list {
  background-color: white;
  border-radius: 20rpx;
}

.record-item {
  display: flex;
  justify-content: space-between;
  padding: 30rpx;
  border-bottom: 1px solid #f5f5f5;
}

.record-item:last-child {
  border-bottom: none;
}

.record-info {
  flex: 1;
}

.record-title {
  font-size: 32rpx;
  margin-bottom: 10rpx;
  color: #333;
  display: block;
}

.record-date {
  font-size: 24rpx;
  color: #999;
  display: block;
}

.record-amount {
  font-size: 36rpx;
  font-weight: 500;
  color: #FF7E00;
  display: block;
  text-align: right;
}

.record-status {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  background-color: #f1f1f1;
  color: #666;
  text-align: center;
  margin-top: 10rpx;
  display: inline-block;
}

.record-status.overdue {
  background-color: #FEE5E5;
  color: #FF5151;
}

.record-status.paid {
  background-color: #E5F7F2;
  color: #33B19E;
}

.empty-records {
  padding: 60rpx 0;
  text-align: center;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.banner {
  border-radius: 20rpx;
  overflow: hidden;
  margin: 0 30rpx 40rpx;
}

.banner-img {
  width: 100%;
  height: 240rpx;
  border-radius: 20rpx;
}

.guide-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 30rpx;
  padding: 20rpx 0;
}

.guide-item {
  background-color: #FFFFFF;
  border-radius: 20rpx;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  transition: transform 0.3s;
}

.guide-item:active {
  transform: scale(0.98);
}

.guide-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
  background-color: #33B19E;
  box-shadow: 0 8rpx 16rpx rgba(51, 177, 158, 0.2);
}

.guide-icon-guide {
  background: linear-gradient(135deg, #33B19E, #28C76F);
}

.guide-icon-safety {
  background: linear-gradient(135deg, #FF9F43, #FFB976);
}

.guide-icon-faq {
  background: linear-gradient(135deg, #4A8CFF, #73A6FF);
}

.guide-icon-service {
  background: linear-gradient(135deg, #EA5455, #F08182);
}

.guide-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 10rpx;
}

.guide-desc {
  font-size: 24rpx;
  color: #999999;
  text-align: center;
}
</style> 