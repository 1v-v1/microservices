<template>
  <view class="login-container">
    <view class="login-header">
      <view class="login-logo">
        <uni-icons type="shield-filled" size="40" color="#ffffff"></uni-icons>
      </view>
      <text class="login-welcome">欢迎使用极速贷</text>
      <text class="login-desc">一站式信用借贷服务平台</text>
    </view>

    <!-- 登录/注册切换 -->
    <view class="login-tabs">
      <view 
        :class="['login-tab', { active: currentTab === 'login' }]" 
        @click="switchTab('login')"
      >
        登录
      </view>
      <view 
        :class="['login-tab', { active: currentTab === 'register' }]" 
        @click="switchTab('register')"
      >
        注册
      </view>
    </view>

    <!-- 登录表单 -->
    <view class="login-form" v-if="currentTab === 'login'">
      <view class="login-input-group">
        <input 
          type="text" 
          class="login-input" 
          placeholder="请输入用户名" 
          v-model="loginForm.username"
        />
      </view>

      <view class="login-input-group">
        <input 
          type="password" 
          class="login-input" 
          placeholder="请输入密码" 
          v-model="loginForm.password"
        />
      </view>

      <button class="login-btn" @click="handleLogin">登录</button>
    </view>

    <!-- 注册表单 -->
    <view class="login-form" v-if="currentTab === 'register'">
      <view class="login-input-group">
        <input 
          type="text" 
          class="login-input" 
          placeholder="请输入用户名" 
          v-model="registerForm.username"
        />
      </view>

      <view class="login-input-group">
        <input 
          type="password" 
          class="login-input" 
          placeholder="请输入密码" 
          v-model="registerForm.password"
        />
      </view>

      <view class="login-input-group">
        <input 
          type="password" 
          class="login-input" 
          placeholder="请确认密码" 
          v-model="registerForm.confirmPassword"
        />
      </view>

      <button class="login-btn" @click="handleRegister">注册</button>
    </view>

    <view class="other-login">
      <view class="other-login-title">其他登录方式</view>
      <view class="other-login-items">
        <view class="other-login-item" @click="loginByWechat">
          <view class="other-login-icon">
            <uni-icons type="weixin" size="20" color="#09BB07"></uni-icons>
          </view>
          <text>微信</text>
        </view>
      </view>
    </view>

    <view class="agreement">
      <checkbox-group @change="checkboxChange">
        <label>
          <checkbox :checked="agreed" style="transform:scale(0.7)"/>
          <text>我已阅读并同意</text>
          <text @click.stop="openAgreement('user')" class="agreement-link">《用户协议》</text>和
          <text @click.stop="openAgreement('privacy')" class="agreement-link">《隐私政策》</text>
        </label>
      </checkbox-group>
    </view>
  </view>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      currentTab: 'login', // 默认显示登录页
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      agreed: true
    };
  },
  methods: {
    ...mapActions('user', ['login', 'register']),
    
    // 切换登录/注册Tab
    switchTab(tab) {
      this.currentTab = tab;
    },
    
    // 处理登录
    handleLogin() {
      if (!this.loginForm.username) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        });
        return;
      }
      
      if (!this.loginForm.password) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        });
        return;
      }
      
      if (!this.agreed) {
        uni.showToast({
          title: '请同意用户协议和隐私政策',
          icon: 'none'
        });
        return;
      }
      
      uni.showLoading({
        title: '登录中...'
      });
      
      // 调用登录action
      this.login({
        username: this.loginForm.username, 
        password: this.loginForm.password
      }).then(res => {
        uni.hideLoading();
        uni.showToast({
          title: res.message,
          icon: 'success',
          duration: 1500,
          success: () => {
            setTimeout(() => {
              uni.switchTab({
                url: '/pages/index/index'
              });
            }, 800);
          }
        });
      }).catch(err => {
        uni.hideLoading();
        uni.showToast({
          title: '登录失败: ' + (err.message || '未知错误'),
          icon: 'none'
        });
      });
    },
    
    // 处理注册
    handleRegister() {
      if (!this.registerForm.username) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        });
        return;
      }
      
      if (!this.registerForm.password) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        });
        return;
      }
      
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        uni.showToast({
          title: '两次输入的密码不一致',
          icon: 'none'
        });
        return;
      }
      
      if (!this.agreed) {
        uni.showToast({
          title: '请同意用户协议和隐私政策',
          icon: 'none'
        });
        return;
      }
      
      uni.showLoading({
        title: '注册中...'
      });
      
      // 调用注册action
      this.register({
        username: this.registerForm.username, 
        password: this.registerForm.password
      }).then(res => {
        uni.hideLoading();
        uni.showToast({
          title: res.message,
          icon: 'success',
          duration: 1500,
          success: () => {
            // 注册成功，切换到登录页
            setTimeout(() => {
              this.switchTab('login');
              this.loginForm.username = this.registerForm.username;
              this.loginForm.password = '';
            }, 800);
          }
        });
      }).catch(err => {
        uni.hideLoading();
        uni.showToast({
          title: '注册失败: ' + (err.message || '未知错误'),
          icon: 'none'
        });
      });
    },
    
    // 微信登录
    loginByWechat() {
      uni.showToast({
        title: '微信登录功能开发中',
        icon: 'none'
      });
    },
    
    // 复选框状态变化
    checkboxChange(e) {
      this.agreed = e.detail.value.length > 0;
    },
    
    // 打开协议
    openAgreement(type) {
      const title = type === 'user' ? '用户协议' : '隐私政策';
      uni.navigateTo({
        url: `/pages/agreement/agreement?type=${type}&title=${title}`
      });
    }
  }
};
</script>

<style lang="scss">
.login-container {
  padding: 40rpx 30rpx;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.login-header {
  text-align: center;
  margin-top: 60rpx;
  margin-bottom: 80rpx;
}

.login-logo {
  width: 160rpx;
  height: 160rpx;
  background-color: #33B19E;
  border-radius: 40rpx;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
  box-shadow: 0 10rpx 30rpx rgba(51, 177, 158, 0.3);
}

.login-welcome {
  font-size: 48rpx;
  font-weight: 600;
  margin-bottom: 10rpx;
  display: block;
}

.login-desc {
  color: #999;
  font-size: 28rpx;
  display: block;
}

/* 登录/注册标签切换 */
.login-tabs {
  display: flex;
  margin-bottom: 40rpx;
  border-bottom: 1px solid #eee;
}

.login-tab {
  flex: 1;
  text-align: center;
  font-size: 32rpx;
  color: #999;
  padding: 20rpx 0;
  position: relative;
}

.login-tab.active {
  color: #33B19E;
  font-weight: 500;
}

.login-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 25%;
  width: 50%;
  height: 4rpx;
  background-color: #33B19E;
  border-radius: 2rpx;
}

.login-form {
  margin-top: 40rpx;
}

.login-input-group {
  position: relative;
  margin-bottom: 40rpx;
}

.login-input {
  width: 100%;
  height: 110rpx;
  border: 1px solid #eee;
  border-radius: 20rpx;
  padding: 0 30rpx;
  font-size: 32rpx;
  background-color: #f9f9f9;
}

.login-input:focus {
  border-color: #33B19E;
  box-shadow: 0 0 0 4rpx rgba(51, 177, 158, 0.2);
  outline: none;
}

.login-btn {
  width: 100%;
  height: 110rpx;
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
  border-radius: 20rpx;
  font-size: 36rpx;
  font-weight: 500;
  margin-top: 40rpx;
  box-shadow: 0 10rpx 30rpx rgba(51, 177, 158, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.other-login {
  text-align: center;
  margin-top: 60rpx;
}

.other-login-title {
  color: #999;
  font-size: 28rpx;
  margin-bottom: 40rpx;
  position: relative;
}

.other-login-title::before,
.other-login-title::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 30%;
  height: 1rpx;
  background-color: #eee;
}

.other-login-title::before {
  left: 0;
}

.other-login-title::after {
  right: 0;
}

.other-login-items {
  display: flex;
  justify-content: center;
}

.other-login-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #666;
  font-size: 24rpx;
}

.other-login-icon {
  width: 90rpx;
  height: 90rpx;
  border-radius: 50%;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.agreement {
  margin-top: 40rpx;
  text-align: center;
  font-size: 24rpx;
  color: #999;
}

.agreement-link {
  color: #33B19E;
  text-decoration: none;
}
</style> 