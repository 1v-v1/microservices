<template>
  <view class="borrow-container">
    <view class="page-title">申请借款</view>

    <!-- 步骤条 -->
    <view class="steps-bar">
      <view :class="['step', { active: currentStep >= 1, completed: currentStep > 1 }]">
        <view class="step-circle">1</view>
        <view class="step-text">填写信息</view>
      </view>
      <view :class="['step', { active: currentStep >= 2, completed: currentStep > 2 }]">
        <view class="step-circle">2</view>
        <view class="step-text">确认借款</view>
      </view>
      <view :class="['step', { active: currentStep >= 3 }]">
        <view class="step-circle">3</view>
        <view class="step-text">放款成功</view>
      </view>
    </view>

    <!-- 步骤1：填写信息 -->
    <view class="step-content" v-if="currentStep === 1">
      <!-- 信用分提示 -->
      <view class="credit-info-card">
        <view class="credit-header">
          <uni-icons type="info" size="20" color="#33B19E"></uni-icons>
          <text class="credit-title">您的信用信息</text>
        </view>
        <view class="credit-details">
          <view class="credit-item">
            <text class="credit-label">当前信用分</text>
            <text :class="['credit-value', getCreditClass(userInfo.creditScore)]">
              {{userInfo.creditScore || 700}}分
            </text>
          </view>
          <view class="credit-item">
            <text class="credit-label">信用等级</text>
            <text :class="['credit-level', getCreditClass(userInfo.creditScore)]">
              {{getCreditLevel(userInfo.creditScore)}}
            </text>
          </view>
        </view>
        <view class="credit-notice" v-if="needManualApproval">
          <uni-icons type="info-filled" size="16" color="#FF7E00"></uni-icons>
          <text>您的信用分低于700分，申请后需要人工审批，请耐心等待</text>
        </view>
        <view class="credit-notice success" v-else>
          <uni-icons type="checkmarkempty" size="16" color="#33B19E"></uni-icons>
          <text>您的信用分达标，申请后将自动审批通过</text>
        </view>
      </view>
      
      <!-- 借款金额 -->
      <view class="borrow-card">
        <view class="card-title">借款金额</view>

        <view class="amount-display">
          <view class="amount-value">¥ <text>{{formatAmount(amount)}}</text></view>
        </view>

        <view class="range-slider">
          <slider 
            :min="2000" 
            :max="50000" 
            :step="1000" 
            :value="amount" 
            @change="onSliderChange" 
            activeColor="#33B19E"
            backgroundColor="#f1f1f1"
            block-color="#FF7E00"
            block-size="24"
          />
        </view>

        <view class="range-limits">
          <text>¥2,000</text>
          <text>¥50,000</text>
        </view>
      </view>

      <!-- 借款期限 -->
      <view class="borrow-card">
        <view class="card-title">借款期限</view>

        <view class="term-options">
          <view 
            v-for="(term, index) in terms" 
            :key="index"
            :class="['term-option', { active: term.days === selectedTerm }]"
            @click="selectTerm(term.days)"
          >{{term.text}}</view>
        </view>
      </view>

      <!-- 下一步按钮 -->
      <button class="confirm-btn" @click="goToStep(2)">下一步</button>
    </view>

    <!-- 步骤2：确认借款 -->
    <view class="step-content" v-if="currentStep === 2">
      <view class="borrow-card">
        <view class="card-title">借款详情</view>

        <view class="fee-details">
          <view class="fee-item">
            <text>借款金额</text>
            <text>¥{{formatAmount(amount)}}</text>
          </view>
          <view class="fee-item">
            <text>借款期限</text>
            <text>{{getTermText(selectedTerm)}}</text>
          </view>
          <view class="fee-item">
            <text>手续费</text>
            <text>¥{{formatAmount(fee)}}</text>
          </view>
          <view class="fee-item">
            <text>利息</text>
            <text>¥{{formatAmount(interest)}}</text>
          </view>
          <view class="fee-item">
            <text>到期还款日</text>
            <text>{{dueDate}}</text>
          </view>
          <view class="fee-total">
            <text>到期还款总额</text>
            <text>¥{{formatAmount(totalAmount)}}</text>
          </view>
        </view>

        <view class="rate-info">
          <uni-icons type="info" size="16" color="#FF7E00"></uni-icons>
          <text>年化利率3.75%，期限内利息已包含在手续费中</text>
        </view>

        <!-- 还款方式选择 -->
        <view class="repay-type-selector">
          <view class="card-title">还款方式</view>
          <view class="repay-type-options">
            <view 
              :class="['repay-type-option', { active: repayType === 'equal-principal' }]"
              @click="selectRepayType('equal-principal')"
            >
              等额本金
              <view class="badge">荐</view>
            </view>
            <view 
              :class="['repay-type-option', { active: repayType === 'equal-installment' }]"
              @click="selectRepayType('equal-installment')"
            >
              等额本息
            </view>
          </view>
          <view class="repay-type-desc">
            <text v-if="repayType === 'equal-principal'">
              等额本金：每月归还同等数额的本金和剩余贷款在该月所产生的利息，本金固定，利息递减。随着本金逐渐归还，需还款总额递减。
            </text>
            <text v-else>
              等额本息：每月以相等的金额偿还贷款本息，本息之和相同，但本金逐月增加，利息逐月减少。月供稳定，更容易规划每月支出。
            </text>
          </view>
        </view>
      </view>

      <!-- 按钮组 -->
      <view class="button-group">
        <button class="back-btn" @click="goToStep(1)">上一步</button>
        <button class="confirm-btn" @click="confirmBorrow">确认借款</button>
      </view>

      <view class="borrow-info">
        点击确认借款，表示您已阅读并同意<text class="link" @click="openAgreement">《借款协议》</text>
      </view>
    </view>

    <!-- 步骤3：借款成功 -->
    <view class="step-content" v-if="currentStep === 3">
      <view class="success-container">
        <!-- 自动批准情况 -->
        <view v-if="!approvalResult.need_manual_approval" class="auto-approved">
          <view class="success-icon">
            <uni-icons type="checkmarkempty" size="40" color="#33B19E"></uni-icons>
          </view>
          <view class="success-title">借款申请成功</view>
          <view class="success-desc">预计30分钟内放款至您的银行卡</view>
        </view>
        
        <!-- 人工审批情况 -->
        <view v-else class="manual-approval">
          <view class="approval-icon">
            <uni-icons type="info" size="40" color="#FF7E00"></uni-icons>
          </view>
          <view class="approval-title">借款申请已提交</view>
          <view class="approval-desc">
            因您的信用分为{{approvalResult.credit_score}}分（低于700分），需要人工审批
          </view>
          <view class="approval-notice">
            <view class="notice-item">
              <uni-icons type="calendar" size="16" color="#666"></uni-icons>
              <text>预计审批时间：1-2个工作日</text>
            </view>
            <view class="notice-item">
              <uni-icons type="phone" size="16" color="#666"></uni-icons>
              <text>审批结果将通过短信通知您</text>
            </view>
            <view class="notice-item">
              <uni-icons type="loop" size="16" color="#666"></uni-icons>
              <text>您可在"我的借款"中查看审批进度</text>
            </view>
          </view>
        </view>

        <view class="success-details">
          <view class="detail-item">
            <text>借款金额</text>
            <text>¥{{formatAmount(amount)}}</text>
          </view>
          <view class="detail-item" v-if="!approvalResult.need_manual_approval">
            <text>到账银行卡</text>
            <text>{{userInfo.bankName || '招商银行'}}({{getMaskedBankCard()}})</text>
          </view>
          <view class="detail-item" v-if="!approvalResult.need_manual_approval">
            <text>到期还款日</text>
            <text>{{dueDate}}</text>
          </view>
          <view class="detail-item">
            <text>申请状态</text>
            <text :class="approvalResult.need_manual_approval ? 'status-pending' : 'status-approved'">
              {{approvalResult.need_manual_approval ? '待审批' : '已批准'}}
            </text>
          </view>
        </view>

        <!-- 还款计划 - 只有自动批准才显示 -->
        <view class="repayment-plan-container" v-if="!approvalResult.need_manual_approval">
          <view class="repayment-plan-toggle" @click="toggleRepaymentPlan">
            <text>{{repaymentPlanOpen ? '收起还款计划' : '查看还款计划'}}</text>
            <view :class="['toggle-icon', { open: repaymentPlanOpen }]">
              <uni-icons type="bottom" size="14" color="#33B19E"></uni-icons>
            </view>
          </view>

          <view :class="['repayment-plan-table', { open: repaymentPlanOpen }]">
            <!-- 等额本金表格 -->
            <view v-if="repayType === 'equal-principal'">
              <scroll-view scroll-x="true" scroll-y="true" class="scroll-view-table">
                <view class="repayment-table">
                  <view class="table-header">
                    <view class="th">期数</view>
                    <view class="th">还款日期</view>
                    <view class="th">月供(元)</view>
                    <view class="th">本金(元)</view>
                    <view class="th">利息(元)</view>
                  </view>
                  <view class="table-body">
                    <view class="table-row" v-for="(item, index) in repaymentPlan.plan" :key="index">
                      <view class="td">{{item.month}}</view>
                      <view class="td">{{item.paymentDate}}</view>
                      <view class="td">¥{{item.payment}}</view>
                      <view class="td">¥{{item.principal}}</view>
                      <view class="td">¥{{item.interest}}</view>
                    </view>
                    <view class="table-row total-row">
                      <view class="td">合计</view>
                      <view class="td"></view>
                      <view class="td">¥{{repaymentPlan.totalPayment}}</view>
                      <view class="td">¥{{repaymentPlan.totalPrincipal}}</view>
                      <view class="td">¥{{repaymentPlan.totalInterest}}</view>
                    </view>
                  </view>
                </view>
              </scroll-view>
            </view>
          </view>
        </view>

        <view class="home-button-container">
          <button class="confirm-btn" @click="backToHome">返回首页</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { formatAmount, formatDate, calculateEqualPrincipal, calculateEqualInstallment } from '@/common/utils';
import { mapState, mapActions } from 'vuex';

export default {
  data() {
    return {
      currentStep: 1,
      amount: 10000, // 借款金额
      selectedTerm: 30, // 所选期限（天）
      terms: [
        { days: 7, text: '7天' },
        { days: 14, text: '14天' },
        { days: 30, text: '30天' },
        { days: 90, text: '3个月' },
        { days: 180, text: '6个月' },
        { days: 365, text: '12个月' }
      ],
      repayType: 'equal-principal', // 还款方式：等额本金
      fee: 0, // 手续费
      interest: 0, // 利息
      dueDate: '', // 到期日
      totalAmount: 0, // 总还款金额
      repaymentPlanOpen: false, // 还款计划是否展开
      repaymentPlan: null, // 还款计划数据
      loanId: '', // 借款ID
      loading: false, // 加载状态
      approvalResult: {} // 审批结果
    };
  },
  computed: {
    ...mapState({
      userInfo: state => state.user.userInfo || {}
    }),
    
    // 是否需要人工审批
    needManualApproval() {
      const creditScore = parseInt(this.userInfo.creditScore || 700);
      return creditScore < 700;
    }
  },
  mounted() {
    this.calculateFees();
  },
  methods: {
    ...mapActions('loan', ['applyLoan']),
    formatAmount,
    
    // 滑块改变事件
    onSliderChange(e) {
      this.amount = e.detail.value;
      this.calculateFees();
    },
    
    // 选择期限
    selectTerm(days) {
      this.selectedTerm = days;
      this.calculateFees();
    },
    
    // 选择还款方式
    selectRepayType(type) {
      this.repayType = type;
      this.calculateRepaymentPlan();
    },
    
    // 获取期限文本
    getTermText(days) {
      const term = this.terms.find(t => t.days === days);
      return term ? term.text : days + '天';
    },
    
    // 计算费用
    calculateFees() {
      // 手续费（按借款金额的3.75%计算）
      this.fee = this.amount * 0.0375;
      
      // 利息（年化3.75%，按天计息）
      const annualRate = 0.0375;
      this.interest = this.amount * annualRate * this.selectedTerm / 365;
      
      // 计算到期日
      const today = new Date();
      const dueDate = new Date(today);
      dueDate.setDate(today.getDate() + this.selectedTerm);
      this.dueDate = formatDate(dueDate);
      
      // 计算总还款金额
      this.totalAmount = this.amount + this.fee + this.interest;
      
      // 计算还款计划
      this.calculateRepaymentPlan();
    },
    
    // 计算还款计划
    calculateRepaymentPlan() {
      // 将天数转换为月数
      let months = 1;
      
      // 根据不同的期限计算月数
      if (this.selectedTerm === 7 || this.selectedTerm === 14) {
        months = 1; // 不足1个月按1个月算
      } else if (this.selectedTerm === 30) {
        months = 1;
      } else if (this.selectedTerm === 90) {
        months = 3;
      } else if (this.selectedTerm === 180) {
        months = 6;
      } else if (this.selectedTerm === 365) {
        months = 12;
      } else {
        months = Math.max(1, Math.ceil(this.selectedTerm / 30));
      }
      
      if (this.repayType === 'equal-principal') {
        // 等额本金
        this.repaymentPlan = calculateEqualPrincipal(this.amount, months, 0.0375);
      } else {
        // 等额本息
        this.repaymentPlan = calculateEqualInstallment(this.amount, months, 0.0375);
      }
    },
    
    // 切换到指定步骤
    goToStep(step) {
      if (step === 2) {
        // 验证第一步数据
        if (this.amount < 2000 || this.amount > 50000) {
          uni.showToast({
            title: '请选择2,000-50,000元之间的借款金额',
            icon: 'none'
          });
          return;
        }
        
        // 计算还款计划
        this.calculateRepaymentPlan();
      }
      
      this.currentStep = step;
    },
    
    // 确认借款
    confirmBorrow() {
      // 判断是否已完善个人资料
      if (!this.userInfo.isProfileCompleted) {
        uni.showModal({
          title: '提示',
          content: '您需要先完善个人资料才能借款',
          confirmText: '去完善',
          success: (res) => {
            if (res.confirm) {
              uni.navigateTo({
                url: '/pages/user-profile/user-profile'
              });
            }
          }
        });
        return;
      }
      
      // 避免重复提交
      if (this.loading) return;
      
      this.loading = true;
      uni.showLoading({ title: '申请处理中...' });
      
      // 准备借款数据
      const loanData = {
        amount: this.amount,
        term: this.selectedTerm, // 直接传递天数或月数
        repayType: this.repayType // 传递还款方式（等额本金或等额本息）
      };
      
      // 调用借款API
      this.applyLoan(loanData).then(res => {
        this.loading = false;
        uni.hideLoading();
        
        // 保存审批结果
        this.approvalResult = res;
        
        if (res.approval_result === 1) {
          // 自动批准成功
          this.loanId = res.loan_id;
          
          // 生成还款计划 - 使用一致的月数计算方式
          let months = 1;
          if (this.selectedTerm === 7 || this.selectedTerm === 14) {
            months = 1;
          } else if (this.selectedTerm === 30) {
            months = 1;
          } else if (this.selectedTerm === 90) {
            months = 3;
          } else if (this.selectedTerm === 180) {
            months = 6;
          } else if (this.selectedTerm === 365) {
            months = 12;
          } else {
            months = Math.max(1, Math.ceil(this.selectedTerm / 30));
          }
          
          if (this.repayType === 'equal-principal') {
            this.repaymentPlan = calculateEqualPrincipal(this.amount, months, 0.0412); // 使用API返回的利率
          } else {
            this.repaymentPlan = calculateEqualInstallment(this.amount, months, 0.0412); // 使用API返回的利率
          }
          
          // 前往成功页
          this.goToStep(3);
          
          // 弹出提示
          uni.showToast({
            title: '借款申请成功',
            icon: 'success'
          });
        } else if (res.approval_result === 2) {
          // 需要人工审批
          this.loanId = res.loan_id;
          
          // 前往成功页（显示待审批状态）
          this.goToStep(3);
          
          // 弹出提示
          uni.showToast({
            title: '申请已提交，请等待审批',
            icon: 'none'
          });
        } else {
          // 借款失败
          uni.showModal({
            title: '申请失败',
            content: res.message || '借款审核未通过，请检查您的借款条件',
            showCancel: false
          });
        }
      }).catch(err => {
        this.loading = false;
        uni.hideLoading();
        uni.showModal({
          title: '借款失败',
          content: err.message || '请求出错，请稍后再试',
          showCancel: false
        });
      });
    },
    
    // 切换还款计划显示
    toggleRepaymentPlan() {
      this.repaymentPlanOpen = !this.repaymentPlanOpen;
    },
    
    // 打开借款协议
    openAgreement() {
      uni.navigateTo({
        url: '/pages/agreement/agreement?type=loan'
      });
    },
    
    // 返回首页
    backToHome() {
      uni.switchTab({
        url: '/pages/index/index'
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
    
    getCreditClass(score) {
      const numScore = parseInt(score) || 700;
      if (numScore >= 700) return 'excellent';
      if (numScore >= 650) return 'good';
      if (numScore >= 600) return 'fair';
      if (numScore >= 550) return 'pass';
      return 'poor';
    },
    
    // 获取脱敏银行卡号
    getMaskedBankCard() {
      const bankCard = this.userInfo.bankCard || '';
      if (bankCard.length >= 4) {
        return bankCard.slice(-4);
      }
      return '****';
    }
  }
};
</script>

<style lang="scss">
.borrow-container {
  padding: 30rpx;
  padding-bottom: 120rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: 600;
  margin-bottom: 40rpx;
  color: #333;
  text-align: center;
}

.steps-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 60rpx;
  position: relative;
}

.steps-bar::before {
  content: "";
  position: absolute;
  top: 30rpx;
  left: 80rpx;
  right: 80rpx;
  height: 4rpx;
  background-color: #eee;
  z-index: 1;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
  flex: 1;
}

.step-circle {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background-color: #f1f1f1;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  margin-bottom: 16rpx;
  position: relative;
}

.step.active .step-circle {
  background-color: #33B19E;
  color: #fff;
}

.step.completed .step-circle {
  background-color: #33B19E;
  color: #fff;
  &:after {
    content: "✓";
    position: absolute;
  }
}

.step-text {
  font-size: 24rpx;
  color: #999;
}

.step.active .step-text {
  color: #33B19E;
  font-weight: 500;
}

.borrow-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 40rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: 500;
  margin-bottom: 30rpx;
  color: #333;
}

.amount-display {
  text-align: center;
  margin-bottom: 40rpx;
}

.amount-value {
  font-size: 72rpx;
  font-weight: 600;
  color: #FF7E00;
}

.range-slider {
  width: 100%;
  margin-bottom: 20rpx;
}

.range-limits {
  display: flex;
  justify-content: space-between;
  font-size: 24rpx;
  color: #999;
}

.term-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-top: 30rpx;
}

.term-option {
  flex: 1;
  min-width: calc(33.33% - 20rpx);
  height: 80rpx;
  border: 1px solid #eee;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #666;
  background-color: #f9f9f9;
}

.term-option.active {
  background-color: #33B19E;
  color: #fff;
  border-color: #33B19E;
}

.fee-details {
  margin-top: 30rpx;
}

.fee-item {
  display: flex;
  justify-content: space-between;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 20rpx;
}

.fee-total {
  display: flex;
  justify-content: space-between;
  font-size: 32rpx;
  font-weight: 500;
  padding-top: 20rpx;
  border-top: 1px dashed #eee;
  margin-top: 20rpx;
}

.rate-info {
  background-color: #FFF8E6;
  border-radius: 20rpx;
  padding: 24rpx 30rpx;
  font-size: 26rpx;
  color: #FF7E00;
  margin-top: 30rpx;
  display: flex;
  align-items: center;
}

.rate-info text {
  margin-left: 16rpx;
}

.confirm-btn {
  width: 100%;
  height: 110rpx;
  background: linear-gradient(to right, #FF7E00, #FF5500);
  color: #fff;
  border: none;
  border-radius: 20rpx;
  font-size: 36rpx;
  font-weight: 500;
  margin-top: 40rpx;
  box-shadow: 0 10rpx 30rpx rgba(255, 126, 0, 0.3);
}

.button-group {
  display: flex;
  gap: 20rpx;
}

.back-btn {
  width: 25%;
  height: 110rpx;
  background-color: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 20rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-top: 40rpx;
}

.button-group .confirm-btn {
  width: 75%;
}

.borrow-info {
  font-size: 24rpx;
  color: #999;
  text-align: center;
  margin-top: 30rpx;
  line-height: 1.5;
}

.link {
  color: #33B19E;
}

// 还款方式选择
.repay-type-selector {
  margin-top: 30rpx;
}

.repay-type-options {
  display: flex;
  gap: 20rpx;
  background-color: #f9f9f9;
  border-radius: 20rpx;
  padding: 10rpx;
  margin-top: 20rpx;
}

.repay-type-option {
  flex: 1;
  padding: 20rpx 10rpx;
  text-align: center;
  font-size: 28rpx;
  color: #666;
  border-radius: 20rpx;
  position: relative;
  transition: all 0.3s ease;
}

.repay-type-option.active {
  background-color: #fff;
  color: #33B19E;
  font-weight: 500;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.repay-type-option .badge {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  width: 36rpx;
  height: 36rpx;
  background-color: #FF5151;
  color: #fff;
  border-radius: 50%;
  font-size: 20rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

.repay-type-desc {
  font-size: 24rpx;
  color: #999;
  margin-top: 20rpx;
  padding: 20rpx;
  background-color: #f5f5f5;
  border-radius: 20rpx;
  border-left: 6rpx solid #33B19E;
  line-height: 1.5;
}

// 成功页面样式
.success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx;
  position: relative;
}

.success-icon {
  width: 160rpx;
  height: 160rpx;
  background-color: #E5F7F2;
  border-radius: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 40rpx;
}

.success-title {
  font-size: 48rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
}

.success-desc {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 60rpx;
}

.success-details {
  background-color: #f9f9f9;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 60rpx;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 20rpx;
}

.detail-item:last-child {
  margin-bottom: 0;
}

// 还款计划表
.repayment-plan-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 24rpx 0;
  background: none;
  border: none;
  color: #33B19E;
  font-size: 28rpx;
  font-weight: 500;
  margin-top: 30rpx;
  border-top: 1px solid #f0f0f0;
}

.toggle-icon {
  transition: transform 0.3s ease;
}

.toggle-icon.open {
  transform: rotate(180deg);
}

.repayment-plan-container {
  width: 100%;
  margin-bottom: 30rpx;
}

.repayment-plan-table {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
  width: 100%;
}

.repayment-plan-table.open {
  margin-top: 20rpx;
  max-height: 600rpx;
  overflow-y: auto;
}

/* 新的滚动表格样式 */
.scroll-view-table {
  width: 100%;
  white-space: nowrap;
}

.repayment-table {
  min-width: 750rpx;
  width: 200%;
  display: inline-block;
  border: 1px solid #eee;
  border-radius: 10rpx;
  overflow: hidden;
}

.table-header {
  display: flex;
  background-color: #f8f8f8;
}

.table-row {
  display: flex;
  border-top: 1px solid #f0f0f0;
}

.total-row {
  background-color: #f8f8f8;
  font-weight: 500;
}

.th, .td {
  flex: 1;
  padding: 20rpx 10rpx;
  font-size: 24rpx;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.th {
  font-weight: 500;
  color: #666;
}

.td {
  color: #333;
}

.home-button-container {
  width: 100%;
  margin-top: 40rpx;
  position: sticky;
  bottom: 20rpx;
  z-index: 10;
  display: flex;
  justify-content: center;
}

/* 信用分信息卡样式 */
.credit-info-card {
  background: linear-gradient(135deg, #f8fffe 0%, #f0f9ff 100%);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  border: 2rpx solid rgba(51, 177, 158, 0.1);
}

.credit-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.credit-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-left: 12rpx;
}

.credit-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.credit-item {
  flex: 1;
  text-align: center;
}

.credit-label {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 8rpx;
}

.credit-value, .credit-level {
  font-size: 32rpx;
  font-weight: 600;
  display: block;
}

.credit-value.excellent, .credit-level.excellent { color: #67C23A; }
.credit-value.good, .credit-level.good { color: #409EFF; }
.credit-value.fair, .credit-level.fair { color: #E6A23C; }
.credit-value.pass, .credit-level.pass { color: #909399; }
.credit-value.poor, .credit-level.poor { color: #F56C6C; }

.credit-notice {
  display: flex;
  align-items: center;
  padding: 16rpx 20rpx;
  border-radius: 12rpx;
  background-color: rgba(255, 126, 0, 0.1);
  border: 1rpx solid rgba(255, 126, 0, 0.2);
}

.credit-notice.success {
  background-color: rgba(51, 177, 158, 0.1);
  border-color: rgba(51, 177, 158, 0.2);
}

.credit-notice text {
  font-size: 26rpx;
  color: #666;
  margin-left: 8rpx;
  line-height: 1.4;
}

/* 人工审批页面样式 */
.manual-approval {
  text-align: center;
}

.approval-icon {
  width: 160rpx;
  height: 160rpx;
  background-color: #FFF8E6;
  border-radius: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 40rpx;
}

.approval-title {
  font-size: 48rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
}

.approval-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 40rpx;
}

.approval-notice {
  background-color: #f8f9fa;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 40rpx;
  text-align: left;
}

.notice-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  font-size: 26rpx;
  color: #666;
}

.notice-item:last-child {
  margin-bottom: 0;
}

.notice-item text {
  margin-left: 12rpx;
}

/* 状态样式 */
.status-approved {
  color: #67C23A;
  font-weight: 600;
}

.status-pending {
  color: #E6A23C;
  font-weight: 600;
}
</style> 