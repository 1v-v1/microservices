<script>
export default {
  onLaunch: function() {
    console.log('App Launch');
    // 初始化逻辑
  },
  onShow: function() {
    console.log('App Show');
  },
  onHide: function() {
    console.log('App Hide');
  }
};
</script>

<style>
/* 全局样式 */
page {
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  background-color: #f7f7f7;
  color: #333;
  margin: 0;
  padding: 0;
  font-size: 28rpx;
  line-height: 1.5;
}

/* 统一按钮样式 */
.btn-primary {
  background-color: #33B19E;
  color: #ffffff;
  border-radius: 20rpx;
}

.btn-secondary {
  background-color: #FF7E00;
  color: #ffffff;
  border-radius: 20rpx;
}

/* 统一卡片样式 */
.card {
  border-radius: 20rpx;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 30rpx;
  background-color: #ffffff;
  padding: 30rpx;
}
</style> 