<template>
  <view class="container">
    <view class="repay-card">
      <view class="repay-info">
        <view class="info-row">
          <text class="info-label">借款明细</text>
          <text class="info-value">{{repayItem.title}}</text>
        </view>
        <view class="info-row">
          <text class="info-label">剩余本金</text>
          <text class="info-value">¥{{formatAmount(repayItem.remaining_amount)}}</text>
        </view>
        <view class="info-row">
          <text class="info-label">还款方式</text>
          <text class="info-value">{{getRepayMethodText(repayItem.repay_method)}}</text>
        </view>
      </view>
    </view>
    
    <!-- 还款计划 -->
    <view class="repay-plan-card" v-if="repaymentPlan.length > 0">
      <view class="card-title">还款计划</view>
      <view class="plan-summary">
        <view class="summary-item">
          <text class="summary-label">剩余期数</text>
          <text class="summary-value">{{remainingPeriods}}期</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">每期金额</text>
          <text class="summary-value">¥{{formatAmount(monthlyPayment)}}</text>
        </view>
      </view>
      
      <view class="plan-list">
        <view 
          v-for="(period, index) in displayPlan" 
          :key="index"
          :class="['plan-item', { 'current': index === 0, 'selected': selectedPeriods > index }]"
        >
          <view class="period-info">
            <text class="period-number">第{{period.period}}期</text>
            <text class="period-date">{{period.dueDate}}</text>
          </view>
          <view class="amount-info">
            <text class="amount">¥{{formatAmount(period.amount)}}</text>
            <view class="amount-detail">
              <text>本金: ¥{{formatAmount(period.principal)}}</text>
              <text>利息: ¥{{formatAmount(period.interest)}}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 还款期数选择 -->
    <view class="period-selector">
      <view class="section-title">选择还款期数</view>
      <view class="period-options">
        <view 
          v-for="option in periodOptions" 
          :key="option.value"
          :class="['period-option', { 'active': selectedPeriods === option.value }]"
          @click="selectPeriods(option.value)"
        >
          <text class="option-text">{{option.label}}</text>
          <text class="option-amount">¥{{formatAmount(option.amount)}}</text>
        </view>
      </view>
    </view>
    
    <!-- 当前还款金额 -->
    <view class="current-repay-card">
      <view class="repay-amount">
        <text class="amount-label">本次还款金额</text>
        <text class="amount-value">¥{{formatAmount(currentRepayAmount)}}</text>
      </view>
      <view class="amount-breakdown" v-if="selectedPeriods > 0">
        <text>包含 {{selectedPeriods}} 期，共计本金 ¥{{formatAmount(totalPrincipal)}}，利息 ¥{{formatAmount(totalInterest)}}</text>
      </view>
    </view>
    
    <view class="section-title">还款方式</view>
    
    <view class="payment-methods">
      <view 
        v-for="(method, index) in paymentMethods" 
        :key="index"
        :class="['payment-method-item', { active: selectedMethod === method.id }]"
        @click="selectPaymentMethod(method.id)"
      >
        <view class="method-icon-wrapper">
          <uni-icons :type="method.icon" :color="method.iconColor" size="24"></uni-icons>
        </view>
        <view class="method-info">
          <text class="method-name">{{method.name}}</text>
          <text class="method-desc">{{method.desc}}</text>
        </view>
        <view class="method-select">
          <view :class="['select-circle', { selected: selectedMethod === method.id }]"></view>
        </view>
      </view>
    </view>
    
    <view class="repay-agreement">
      <view class="checkbox-container" @click="toggleAgreement">
        <view :class="['checkbox', { checked: agreedToTerms }]">
          <uni-icons v-if="agreedToTerms" type="checkmarkempty" size="12" color="#FFFFFF"></uni-icons>
        </view>
      </view>
      <text class="agreement-text">
        我已阅读并同意
        <text class="agreement-link" @click.stop="openAgreement('repayment')">《还款协议》</text>
      </text>
    </view>
    
    <button 
      class="confirm-btn" 
      :disabled="!selectedMethod || !agreedToTerms || selectedPeriods === 0 || currentRepayAmount === 0"
      :class="{ disabled: !selectedMethod || !agreedToTerms || selectedPeriods === 0 || currentRepayAmount === 0 }"
      @click="confirmRepayment"
    >
      确认还款 {{selectedPeriods > 0 ? `(${selectedPeriods}期)` : ''}}
    </button>
  </view>
</template>

<script>
import { formatAmount } from '@/common/utils';
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      repayItem: {}, // 还款项目
      repaymentPlan: [], // 完整还款计划
      selectedPeriods: 1, // 选择的还款期数
      currentRepayAmount: 0, // 当前还款金额
      paymentMethods: [
        {
          id: 'alipay',
          name: '支付宝支付',
          desc: '推荐支付宝用户使用',
          icon: 'wallet',
          iconColor: '#1677FF'
        },
        {
          id: 'wechat',
          name: '微信支付',
          desc: '推荐微信用户使用',
          icon: 'weixin',
          iconColor: '#09BB07'
        },
        {
          id: 'bank',
          name: '银行卡支付',
          desc: '支持大多数银行借记卡',
          icon: 'wallet-filled',
          iconColor: '#722ED1'
        }
      ],
      selectedMethod: 'alipay', // 默认选择支付宝
      agreedToTerms: false // 是否同意条款
    };
  },
  computed: {
    // 剩余期数
    remainingPeriods() {
      return this.repaymentPlan.length;
    },
    
    // 每期还款金额
    monthlyPayment() {
      return this.repaymentPlan.length > 0 ? this.repaymentPlan[0].amount : 0;
    },
    
    // 显示的还款计划（最多显示6期）
    displayPlan() {
      return this.repaymentPlan.slice(0, Math.min(6, this.repaymentPlan.length));
    },
    
    // 期数选择选项
    periodOptions() {
      const options = [];
      const maxPeriods = Math.min(6, this.repaymentPlan.length);
      
      for (let i = 1; i <= maxPeriods; i++) {
        const amount = this.repaymentPlan.slice(0, i).reduce((sum, period) => sum + period.amount, 0);
        options.push({
          value: i,
          label: i === 1 ? '还1期' : `还${i}期`,
          amount: amount
        });
      }
      
      // 添加全部还清选项
      if (this.repaymentPlan.length > 0) {
        const totalAmount = this.repaymentPlan.reduce((sum, period) => sum + period.amount, 0);
        options.push({
          value: this.repaymentPlan.length,
          label: '全部还清',
          amount: totalAmount
        });
      }
      
      return options;
    },
    
    // 总本金
    totalPrincipal() {
      if (this.selectedPeriods === 0) return 0;
      return this.repaymentPlan.slice(0, this.selectedPeriods).reduce((sum, period) => sum + period.principal, 0);
    },
    
    // 总利息
    totalInterest() {
      if (this.selectedPeriods === 0) return 0;
      return this.repaymentPlan.slice(0, this.selectedPeriods).reduce((sum, period) => sum + period.interest, 0);
    }
  },
  onLoad(options) {
    console.log('确认还款页面加载，参数:', options);
    
    // 获取路由参数
    if (options.id && options.amount) {
      // 从本地存储获取完整的还款项目信息
      const repayItemStr = uni.getStorageSync('currentRepayItem');
      console.log('从本地存储获取的还款项目:', repayItemStr);
      
      if (repayItemStr) {
        try {
          this.repayItem = JSON.parse(repayItemStr);
          console.log('解析后的还款项目:', this.repayItem);
          
          // 确保repayItem有必要的信息
          if (!this.repayItem.id) {
            this.repayItem.id = options.id;
          }
          if (!this.repayItem.title) {
            this.repayItem.title = `贷款编号: ${options.id.substring(0, 8)}...`;
          }
          if (!this.repayItem.dueDate) {
            this.repayItem.dueDate = this.repayItem.next_payment_date || '未设置';
          }
          
          console.log('最终的还款项目信息:', this.repayItem);
          
          // 获取还款计划
          this.loadRepaymentPlan();
          
        } catch (e) {
          console.error('解析还款项目信息失败', e);
          this.handleError();
        }
      } else {
        console.log('本地存储中没有还款项目信息');
        this.handleError();
      }
    } else {
      console.error('缺少必要参数，id:', options.id, 'amount:', options.amount);
      this.handleError();
    }
  },
  watch: {
    selectedPeriods(newVal) {
      this.updateCurrentRepayAmount();
    }
  },
  methods: {
    ...mapActions('repay', ['submitRepay', 'getRepayPlan']),
    
    // 格式化金额
    formatAmount,
    
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
    
    // 加载还款计划
    async loadRepaymentPlan() {
      try {
        uni.showLoading({
          title: '加载还款计划...'
        });
        
        console.log('获取还款计划，贷款ID:', this.repayItem.loan_id);
        const plan = await this.getRepayPlan(this.repayItem.loan_id);
        console.log('获取到的还款计划:', plan);
        
        this.repaymentPlan = plan || [];
        this.updateCurrentRepayAmount();
        
        uni.hideLoading();
      } catch (error) {
        console.error('获取还款计划失败:', error);
        uni.hideLoading();
        uni.showToast({
          title: '获取还款计划失败',
          icon: 'none'
        });
      }
    },
    
    // 选择还款期数
    selectPeriods(periods) {
      this.selectedPeriods = periods;
    },
    
    // 更新当前还款金额
    updateCurrentRepayAmount() {
      if (this.selectedPeriods === 0 || this.repaymentPlan.length === 0) {
        this.currentRepayAmount = 0;
        return;
      }
      
      this.currentRepayAmount = this.repaymentPlan
        .slice(0, this.selectedPeriods)
        .reduce((sum, period) => sum + period.amount, 0);
    },
    
    // 处理页面加载错误
    handleError() {
      uni.showToast({
        title: '加载还款信息失败',
        icon: 'none'
      });
      
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
    },
    
    // 选择支付方式
    selectPaymentMethod(methodId) {
      this.selectedMethod = methodId;
    },
    
    // 切换协议同意状态
    toggleAgreement() {
      this.agreedToTerms = !this.agreedToTerms;
    },
    
    // 打开协议页面
    openAgreement(type) {
      uni.navigateTo({
        url: `/pages/agreement/agreement?type=${type}`
      });
    },
    
    // 确认还款
    confirmRepayment() {
      if (!this.selectedMethod || !this.agreedToTerms) {
        uni.showToast({
          title: '请选择支付方式并同意协议',
          icon: 'none'
        });
        return;
      }
      
      if (this.selectedPeriods === 0 || this.currentRepayAmount === 0) {
        uni.showToast({
          title: '请选择还款期数',
          icon: 'none'
        });
        return;
      }
      
      // 显示加载
      uni.showLoading({
        title: '处理中...'
      });
      
      // 根据不同的支付方式处理支付
      switch(this.selectedMethod) {
        case 'alipay':
          this.handleAlipayPayment();
          break;
        case 'wechat':
          this.handleWechatPayment();
          break;
        case 'bank':
          this.handleBankPayment();
          break;
      }
    },
    
    // 处理支付宝支付
    handleAlipayPayment() {
      this.processPayment('alipay');
    },
    
    // 处理微信支付
    handleWechatPayment() {
      this.processPayment('wechat');
    },
    
    // 处理银行卡支付
    handleBankPayment() {
      this.processPayment('bank');
    },
    
    // 统一处理支付流程
    processPayment(paymentType) {
      // 准备分期还款数据
      const repayData = {
        loanId: this.repayItem.id || this.repayItem.loan_id,
        amount: this.currentRepayAmount,
        periods: this.selectedPeriods,
        paymentMethod: paymentType,
        repaymentPlan: this.repaymentPlan.slice(0, this.selectedPeriods)
      };
      
      console.log('提交分期还款数据:', repayData);
      
      // 调用API进行分期还款
      this.submitRepay(repayData)
        .then(async res => {
          console.log('还款响应:', res);
          
          if (res.message === '还款成功') {
            // 还款成功后刷新数据
            try {
              // 刷新还款列表
              await this.$store.dispatch('repay/getRepayList');
              
              // 刷新用户信息（更新待还款金额）
              await this.$store.dispatch('user/getUserInfo');
              
              // 清除本地存储的还款项目
              uni.removeStorageSync('currentRepayItem');
              
              console.log('数据刷新完成');
            } catch (error) {
              console.error('刷新数据失败:', error);
            }
            
            uni.hideLoading();
            
            // 跳转到成功页面
            uni.redirectTo({
              url: `/pages/repay-success/repay-success?amount=${res.amount || this.currentRepayAmount}&periods=${this.selectedPeriods}&remainingAmount=${res.remaining_amount || 0}`
            });
          } else {
            uni.hideLoading();
            uni.showModal({
              title: '提示',
              content: res.message || '还款处理中，请稍后查看结果',
              showCancel: false
            });
          }
        })
        .catch(err => {
          uni.hideLoading();
          console.error('还款失败:', err);
          uni.showModal({
            title: '还款失败',
            content: err.message || '请求失败，请稍后再试',
            showCancel: false
          });
        });
    }
  }
};
</script>

<style lang="scss">
.container {
  padding: 30rpx;
}

.repay-card {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.repay-info {
  
}

.repay-plan-card {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  margin-bottom: 30rpx;
  color: #333;
}

.plan-summary {
  display: flex;
  justify-content: space-between;
  padding: 20rpx;
  background-color: #f8f9fa;
  border-radius: 16rpx;
  margin-bottom: 30rpx;
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 24rpx;
  color: #666;
  display: block;
  margin-bottom: 8rpx;
}

.summary-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #33B19E;
  display: block;
}

.plan-list {
  max-height: 400rpx;
  overflow-y: auto;
}

.plan-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 12rpx;
  background-color: #f8f9fa;
}

.plan-item.current {
  background-color: #E5F7F2;
  border: 1px solid #33B19E;
}

.plan-item.selected {
  background-color: #33B19E;
  color: white;
}

.plan-item.selected .period-date,
.plan-item.selected .amount-detail text {
  color: rgba(255, 255, 255, 0.8);
}

.period-info {
  
}

.period-number {
  font-size: 28rpx;
  font-weight: 500;
  display: block;
  margin-bottom: 6rpx;
}

.period-date {
  font-size: 24rpx;
  color: #666;
  display: block;
}

.amount-info {
  text-align: right;
}

.amount {
  font-size: 30rpx;
  font-weight: 600;
  display: block;
  margin-bottom: 6rpx;
}

.amount-detail {
  display: flex;
  flex-direction: column;
  gap: 2rpx;
}

.amount-detail text {
  font-size: 22rpx;
  color: #666;
}

.period-selector {
  margin-bottom: 30rpx;
}

.period-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-top: 20rpx;
}

.period-option {
  background-color: white;
  border: 2rpx solid #eee;
  border-radius: 16rpx;
  padding: 24rpx 20rpx;
  text-align: center;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.period-option.active {
  border-color: #33B19E;
  background-color: #E5F7F2;
}

.option-text {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.option-amount {
  font-size: 24rpx;
  color: #33B19E;
  font-weight: 600;
  display: block;
}

.current-repay-card {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  text-align: center;
}

.repay-amount {
  margin-bottom: 20rpx;
}

.amount-label {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 16rpx;
}

.amount-value {
  font-size: 56rpx;
  font-weight: 600;
  color: #FF6B35;
}

.amount-breakdown {
  padding: 16rpx;
  background-color: #f8f9fa;
  border-radius: 12rpx;
  font-size: 24rpx;
  color: #666;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
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

.section-title {
  font-size: 32rpx;
  font-weight: 500;
  margin: 30rpx 0 20rpx;
}

.payment-methods {
  background-color: white;
  border-radius: 20rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.payment-method-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1px solid #f5f5f5;
}

.payment-method-item:last-child {
  border-bottom: none;
}

.payment-method-item.active {
  background-color: #F8F8F8;
}

.method-icon-wrapper {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background-color: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
}

.method-info {
  flex: 1;
}

.method-name {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 8rpx;
  display: block;
}

.method-desc {
  font-size: 24rpx;
  color: #999;
  display: block;
}

.method-select {
  padding: 0 10rpx;
}

.select-circle {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  border: 1px solid #ddd;
  box-sizing: border-box;
}

.select-circle.selected {
  border: none;
  background-color: #33B19E;
}

.repay-agreement {
  display: flex;
  align-items: center;
  margin: 40rpx 0;
}

.checkbox-container {
  margin-right: 10rpx;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  border: 1px solid #ddd;
  display: flex;
  justify-content: center;
  align-items: center;
}

.checkbox.checked {
  background-color: #33B19E;
  border-color: #33B19E;
}

.agreement-text {
  font-size: 26rpx;
  color: #666;
  flex: 1;
}

.agreement-link {
  color: #33B19E;
}

.confirm-btn {
  width: 100%;
  height: 90rpx;
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
  border-radius: 45rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-top: 20rpx;
}

.confirm-btn.disabled {
  opacity: 0.6;
}
</style> 