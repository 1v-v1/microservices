<template>
  <view class="container">
    <!-- 顶部用户信息 -->
    <view class="user-header">
      <view class="user-avatar">
        <image :src="getAvatarUrl(userInfo.avatar)" mode="aspectFill" @error="onImageError"></image>
        <view class="edit-avatar" @click="changeAvatar">
          <uni-icons type="camera" size="16" color="#FFFFFF"></uni-icons>
        </view>
      </view>
      
      <view class="user-info">
        <text class="username">{{isLoggedIn ? (userInfo.realName || userInfo.username || '用户') : '未登录'}}</text>
        <view class="user-credit">
          <text class="credit-label">信用分</text>
          <text class="credit-value">{{userInfo.creditScore || '- -'}}</text>
        </view>
      </view>
      
      <view class="login-btn-wrapper" v-if="!isLoggedIn">
        <button class="login-btn" @click="goToLogin">马上登录</button>
      </view>
      
      <view class="login-btn-wrapper" v-else-if="!userInfo.isProfileCompleted">
        <button class="login-btn" @click="goToCompleteProfile">完善资料</button>
      </view>
    </view>
    
    <!-- 借贷概览 -->
    <view class="loan-overview" v-if="isLoggedIn">
      <view class="overview-item">
        <view class="overview-value">¥{{formatAmount(userInfo.loanLimit)}}</view>
        <view class="overview-label">可借额度</view>
      </view>
      <view class="divider"></view>
      <view class="overview-item">
        <view class="overview-value">¥{{formatAmount(userInfo.totalBorrowed)}}</view>
        <view class="overview-label">累计借款</view>
      </view>
      <view class="divider"></view>
      <view class="overview-item">
        <view class="overview-value">¥{{formatAmount(userInfo.pendingRepay)}}</view>
        <view class="overview-label">待还借款</view>
      </view>
    </view>
    
    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="section-title">
        <text>我的服务</text>
      </view>
      
      <view class="menu-list">
        <view class="menu-item" @click="navigateTo('/pages/borrow/loan-records')">
          <view class="menu-icon menu-icon-loan">
            <uni-icons type="compose" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">借款记录</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
        
        <view class="menu-item" @click="navigateTo('/pages/repay-history/repay-history')">
          <view class="menu-icon menu-icon-repay">
            <uni-icons type="refreshempty" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">还款记录</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
        
        <view class="menu-item" @click="navigateTo('/pages/bank-card/bank-card')">
          <view class="menu-icon menu-icon-card">
            <uni-icons type="wallet" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">银行卡管理</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
      </view>
    </view>
    
    <view class="menu-section">
      <view class="section-title">
        <text>设置与帮助</text>
      </view>
      
      <view class="menu-list">
        <view class="menu-item" @click="goToCompleteProfile">
          <view class="menu-icon menu-icon-personal">
            <uni-icons type="person" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">个人资料</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
        
        <view class="menu-item" @click="navigateTo('/pages/guide/guide?type=safety')">
          <view class="menu-icon menu-icon-safety">
            <uni-icons type="locked" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">安全中心</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
        
        <view class="menu-item" @click="navigateTo('/pages/guide/guide?type=guide')">
          <view class="menu-icon menu-icon-guide">
            <uni-icons type="help" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">使用帮助</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
        
        <view class="menu-item" @click="navigateTo('/pages/guide/guide?type=service')">
          <view class="menu-icon menu-icon-service">
            <uni-icons type="headphones" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">联系客服</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
        
        <view class="menu-item" @click="navigateTo('/pages/agreement/agreement?type=service')">
          <view class="menu-icon menu-icon-agreement">
            <uni-icons type="paperplane" size="20" color="#FFFFFF"></uni-icons>
          </view>
          <view class="menu-text">服务协议</view>
          <uni-icons type="arrowright" size="14" color="#C8C8C8"></uni-icons>
        </view>
      </view>
    </view>
    
    <!-- 退出登录 -->
    <view class="logout-btn-wrapper" v-if="isLoggedIn">
      <button class="logout-btn" @click="logout">退出登录</button>
    </view>
  </view>
</template>

<script>
import { formatAmount } from '@/common/utils';
import { mapState, mapActions, mapGetters } from 'vuex';

export default {
  data() {
    return {};
  },
  computed: {
    ...mapState({
      userInfo: state => state.user.userInfo || {}
    }),
    isLoggedIn() {
      return !!this.$store.state.user.token;
    }
  },
  onShow() {
    // 每次页面显示时刷新用户信息
    if (this.isLoggedIn) {
      this.getUserInfo();
    }
  },
  methods: {
    ...mapActions('user', ['getUserInfo', 'logout']),
    
    // 格式化金额
    formatAmount,
    
    // 获取头像URL
    getAvatarUrl(avatar) {
      if (!avatar) {
        return '/common/static/default-avatar.svg';
      }
      
      // 如果是完整URL，直接返回
      if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
        return avatar;
      }
      
      // 如果是相对路径，补全为完整URL
      if (avatar.startsWith('/uploads/')) {
        return `http://localhost:8000${avatar}`;
      }
      
      // 其他情况返回默认头像
      return '/common/static/default-avatar.svg';
    },
    
    // 图片加载失败处理
    onImageError(e) {
      console.log('头像加载失败:', e);
      // 如果头像加载失败，更新为默认头像
      this.$store.commit('user/UPDATE_USER_INFO', {
        ...this.userInfo,
        avatar: ''  // 清空avatar，会使用默认头像
      });
    },
    
    // 前往登录页
    goToLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      });
    },
    
    // 前往完善资料页
    goToCompleteProfile() {
      if (!this.isLoggedIn) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        });
        
        setTimeout(() => {
          this.goToLogin();
        }, 1500);
        return;
      }
      
      uni.navigateTo({
        url: '/pages/user-profile/user-profile'
      });
    },
    
    // 导航到指定页面
    navigateTo(url) {
      // 如果需要登录但用户未登录，则先跳转到登录页
      if (!this.isLoggedIn && url !== '/pages/guide/guide' && url !== '/pages/agreement/agreement') {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        });
        setTimeout(() => {
          this.goToLogin();
        }, 1500);
        return;
      }
      
      uni.navigateTo({
        url: url
      });
    },
    
    // 更换头像
    changeAvatar() {
      if (!this.isLoggedIn) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        });
        return;
      }
      
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.uploadAvatar(res.tempFilePaths[0]);
        },
        fail: (err) => {
          console.error('选择图片失败:', err);
          uni.showToast({
            title: '选择图片失败',
            icon: 'none'
          });
        }
      });
    },
    
    // 上传头像
    uploadAvatar(filePath) {
      uni.showLoading({
        title: '上传中...'
      });
      
      // 获取token
      const token = this.$store.state.user.token;
      
      uni.uploadFile({
        url: 'http://localhost:8000/api/user/upload-avatar',
        filePath: filePath,
        name: 'avatar',
        formData: {
          'username': this.userInfo.username || ''
        },
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (uploadRes) => {
          uni.hideLoading();
          
          try {
            const result = JSON.parse(uploadRes.data);
            
            if (result.success) {
              // 立即更新本地用户信息中的头像
              const newAvatarUrl = `http://localhost:8000${result.avatar_url}`;
              this.$store.commit('user/UPDATE_USER_INFO', {
                ...this.userInfo,
                avatar: newAvatarUrl
              });
              
              uni.showToast({
                title: '头像更新成功',
                icon: 'success'
              });
              
              // 延迟一点再刷新用户信息，确保服务器已保存
              setTimeout(() => {
                this.getUserInfo();
              }, 500);
            } else {
              uni.showToast({
                title: result.message || '上传失败',
                icon: 'none'
              });
            }
          } catch (e) {
            console.error('解析响应失败:', e);
            uni.showToast({
              title: '上传失败',
              icon: 'none'
            });
          }
        },
        fail: (err) => {
          uni.hideLoading();
          console.error('上传头像失败:', err);
          uni.showToast({
            title: '上传失败',
            icon: 'none'
          });
        }
      });
    },
    
    // 退出登录
    logout() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 调用退出登录接口
            this.logout();
            
            uni.showToast({
              title: '已退出登录',
              icon: 'success'
            });
          }
        }
      });
    }
  }
};
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background-color: #f7f7f7;
  padding-bottom: 40rpx;
}

/* 用户头部信息 */
.user-header {
  padding: 60rpx 40rpx;
  background: linear-gradient(135deg, #33B19E, #29A28E);
  color: white;
  display: flex;
  align-items: center;
  position: relative;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
  position: relative;
  margin-right: 30rpx;
  
  image {
    width: 100%;
    height: 100%;
  }
}

.edit-avatar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40rpx;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 36rpx;
  font-weight: 600;
  margin-bottom: 10rpx;
  display: block;
}

.user-credit {
  display: flex;
  align-items: center;
}

.credit-label {
  font-size: 24rpx;
  opacity: 0.8;
  margin-right: 10rpx;
}

.credit-value {
  font-size: 28rpx;
  font-weight: 600;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 6rpx 20rpx;
  border-radius: 30rpx;
}

.login-btn-wrapper {
  margin-top: 20rpx;
}

.login-btn {
  background-color: white;
  color: #33B19E;
  font-size: 28rpx;
  padding: 10rpx 30rpx;
  border-radius: 30rpx;
  font-weight: 500;
  box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.1);
  line-height: 1.5;
}

/* 借贷概览 */
.loan-overview {
  margin: 30rpx;
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.overview-item {
  flex: 1;
  text-align: center;
}

.divider {
  width: 1px;
  height: 80rpx;
  background-color: #f1f1f1;
}

.overview-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 10rpx;
}

.overview-label {
  font-size: 24rpx;
  color: #999;
}

/* 菜单部分 */
.menu-section {
  margin: 30rpx;
  background-color: white;
  border-radius: 20rpx;
  margin-bottom: 30rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.section-title {
  padding: 30rpx;
  border-bottom: 1px solid #f8f8f8;
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.menu-list {
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1px solid #f8f8f8;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background-color: #F6FFFE;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.05);
}

.menu-icon-loan {
  background: linear-gradient(135deg, #4A8CFF, #73A6FF);
}

.menu-icon-repay {
  background: linear-gradient(135deg, #33B19E, #28C76F);
}

.menu-icon-card {
  background: linear-gradient(135deg, #FF9F43, #FFB976);
}

.menu-icon-personal {
  background: linear-gradient(135deg, #4A8CFF, #73A6FF);
}

.menu-icon-safety {
  background: linear-gradient(135deg, #FF9F43, #FFB976);
}

.menu-icon-guide {
  background: linear-gradient(135deg, #33B19E, #28C76F);
}

.menu-icon-service {
  background: linear-gradient(135deg, #EA5455, #F08182);
}

.menu-icon-agreement {
  background: linear-gradient(135deg, #4A8CFF, #73A6FF);
}

.menu-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

/* 退出登录按钮 */
.logout-btn-wrapper {
  margin: 60rpx 30rpx;
}

.logout-btn {
  width: 100%;
  height: 90rpx;
  background-color: white;
  color: #FF5151;
  border: 1px solid #FF5151;
  border-radius: 45rpx;
  font-size: 32rpx;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 