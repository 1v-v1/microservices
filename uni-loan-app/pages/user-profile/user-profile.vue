<template>
  <view class="profile-container">
    <view class="profile-header">
      <view class="page-title">完善个人资料</view>
      <view class="page-desc">完善您的个人资料以便更好地使用我们的服务</view>
    </view>

    <view class="form-card">
      <view class="form-item">
        <text class="form-label">真实姓名</text>
        <input 
          type="text" 
          class="form-input" 
          placeholder="请输入您的真实姓名" 
          v-model="profileForm.realName"
        />
      </view>

      <view class="form-item">
        <text class="form-label">身份证号</text>
        <input 
          type="idcard" 
          class="form-input" 
          placeholder="请输入您的身份证号" 
          v-model="profileForm.idCard"
          maxlength="18"
        />
      </view>

      <view class="form-item">
        <text class="form-label">手机号码</text>
        <input 
          type="number" 
          class="form-input" 
          placeholder="请输入您的手机号码" 
          v-model="profileForm.phone"
          maxlength="11"
        />
      </view>

      <view class="form-item">
        <text class="form-label">银行卡号</text>
        <input 
          type="number" 
          class="form-input" 
          placeholder="请输入您的银行卡号" 
          v-model="profileForm.bankCard"
          maxlength="19"
        />
      </view>

      <view class="form-item">
        <text class="form-label">开户银行</text>
        <picker 
          mode="selector" 
          :range="bankList" 
          range-key="name"
          @change="onBankChange"
          class="form-picker"
        >
          <view class="picker-text" :class="{ 'placeholder': !profileForm.bankName }">
            {{ profileForm.bankName || '请选择开户银行' }}
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="form-label">月收入(元)</text>
        <input 
          type="digit" 
          class="form-input" 
          placeholder="请输入您的月收入" 
          v-model="profileForm.monthlyIncome"
        />
      </view>
    </view>

    <button class="submit-btn" @click="submitProfile">保存资料</button>
  </view>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  data() {
    return {
      profileForm: {
        realName: '',
        idCard: '',
        phone: '',
        bankCard: '',
        bankName: '',
        bankCode: '',
        monthlyIncome: ''
      },
      bankList: [
        { name: '中国工商银行', code: 'ICBC' },
        { name: '中国农业银行', code: 'ABC' },
        { name: '中国银行', code: 'BOC' },
        { name: '中国建设银行', code: 'CCB' },
        { name: '交通银行', code: 'COMM' },
        { name: '招商银行', code: 'CMB' },
        { name: '中国邮政储蓄银行', code: 'PSBC' },
        { name: '中信银行', code: 'CITIC' },
        { name: '浦发银行', code: 'SPDB' },
        { name: '兴业银行', code: 'CIB' },
        { name: '中国光大银行', code: 'CEB' },
        { name: '华夏银行', code: 'HXB' },
        { name: '民生银行', code: 'CMBC' }
      ]
    };
  },
  computed: {
    ...mapState({
      userInfo: state => state.user.userInfo || {}
    })
  },
  onLoad() {
    // 如果已有用户信息，预填表单
    if (this.userInfo) {
      if (this.userInfo.realName) this.profileForm.realName = this.userInfo.realName;
      if (this.userInfo.idCard) this.profileForm.idCard = this.userInfo.idCard;
      if (this.userInfo.phone) this.profileForm.phone = this.userInfo.phone;
      if (this.userInfo.bankCard) this.profileForm.bankCard = this.userInfo.bankCard;
      if (this.userInfo.bankName) this.profileForm.bankName = this.userInfo.bankName;
      if (this.userInfo.bankCode) this.profileForm.bankCode = this.userInfo.bankCode;
      if (this.userInfo.monthlyIncome) this.profileForm.monthlyIncome = this.userInfo.monthlyIncome;
    }
  },
  methods: {
    ...mapActions('user', ['updateUserProfile']),
    
    // 选择银行
    onBankChange(e) {
      const index = e.detail.value;
      const bank = this.bankList[index];
      this.profileForm.bankName = bank.name;
      this.profileForm.bankCode = bank.code;
    },
    
    // 提交资料
    submitProfile() {
      // 表单验证
      if (!this.profileForm.realName) {
        uni.showToast({
          title: '请输入真实姓名',
          icon: 'none'
        });
        return;
      }
      
      if (!this.profileForm.idCard) {
        uni.showToast({
          title: '请输入身份证号',
          icon: 'none'
        });
        return;
      }
      
      if (!/^\d{17}(\d|X)$/i.test(this.profileForm.idCard)) {
        uni.showToast({
          title: '身份证号格式不正确',
          icon: 'none'
        });
        return;
      }
      
      if (!this.profileForm.phone) {
        uni.showToast({
          title: '请输入手机号码',
          icon: 'none'
        });
        return;
      }
      
      if (!/^1\d{10}$/.test(this.profileForm.phone)) {
        uni.showToast({
          title: '手机号码格式不正确',
          icon: 'none'
        });
        return;
      }
      
      if (!this.profileForm.bankCard) {
        uni.showToast({
          title: '请输入银行卡号',
          icon: 'none'
        });
        return;
      }
      
      if (!/^\d{16,19}$/.test(this.profileForm.bankCard)) {
        uni.showToast({
          title: '银行卡号格式不正确',
          icon: 'none'
        });
        return;
      }
      
      if (!this.profileForm.bankName) {
        uni.showToast({
          title: '请选择开户银行',
          icon: 'none'
        });
        return;
      }
      
      if (!this.profileForm.monthlyIncome) {
        uni.showToast({
          title: '请输入月收入',
          icon: 'none'
        });
        return;
      }
      
      uni.showLoading({
        title: '保存中...'
      });
      
      // 调用API保存个人资料
      this.updateUserProfile(this.profileForm).then(() => {
        uni.hideLoading();
        uni.showToast({
          title: '资料保存成功',
          icon: 'success',
          duration: 2000,
          success: () => {
            setTimeout(() => {
              uni.navigateBack();
            }, 2000);
          }
        });
      }).catch(err => {
        uni.hideLoading();
        uni.showToast({
          title: '保存失败: ' + (err.message || '未知错误'),
          icon: 'none'
        });
      });
    }
  }
};
</script>

<style lang="scss">
.profile-container {
  padding: 30rpx;
  min-height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-header {
  padding: 30rpx 0;
  margin-bottom: 30rpx;
  text-align: center;
  width: 90%;
}

.page-title {
  font-size: 40rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
}

.page-desc {
  font-size: 28rpx;
  color: #999;
}

.form-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 40rpx;
  width: 90%;
  max-width: 650rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 16rpx;
}

.form-input {
  width: 90%;
  height: 90rpx;
  border: 1px solid #eee;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  background-color: #f9f9f9;
  margin: 0;
  display: block;
}

.form-picker {
  width: 90%;
  height: 90rpx;
  border: 1px solid #eee;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  background-color: #f9f9f9;
  display: flex;
  align-items: center;
  margin: 0;
}

.picker-text {
  color: #333;
}

.placeholder {
  color: #999;
}

.submit-btn {
  width: 90%;
  max-width: 650rpx;
  height: 90rpx;
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
  border-radius: 45rpx;
  font-size: 32rpx;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 40rpx;
  box-shadow: 0 10rpx 30rpx rgba(51, 177, 158, 0.3);
}
</style> 