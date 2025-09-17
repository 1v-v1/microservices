<template>
  <view class="container">
    <view class="guide-header">
      <text class="guide-title">{{guideTitle}}</text>
    </view>
    
    <view class="guide-content">
      <scroll-view scroll-y class="content-scroll">
        <view class="section" v-for="(section, index) in guideSections" :key="index">
          <view class="section-header">
            <view class="section-icon">
              <uni-icons :type="section.icon" size="20" color="#33B19E"></uni-icons>
            </view>
            <text class="section-title">{{section.title}}</text>
          </view>
          <view class="section-content">
            <text class="section-text">{{section.content}}</text>
            <image 
              v-if="section.image" 
              :src="section.image" 
              mode="widthFix" 
              class="section-image"
            ></image>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <view class="guide-footer" v-if="showContactButton">
      <button class="contact-btn" @click="contactCustomerService">联系客服</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      guideType: '', // 指南类型
      guideTitle: '使用指南', // 指南标题
      showContactButton: false, // 是否显示联系客服按钮
      guideSections: [] // 指南内容区块
    };
  },
  onLoad(options) {
    // 获取路由参数
    if (options.type) {
      this.guideType = options.type;
      
      // 设置标题和内容
      this.setGuideContent();
    }
  },
  methods: {
    // 设置指南内容
    setGuideContent() {
      switch(this.guideType) {
        case 'guide':
          this.guideTitle = '新手指南';
          this.guideSections = this.getBeginnerGuide();
          this.showContactButton = false;
          break;
        case 'safety':
          this.guideTitle = '安全中心';
          this.guideSections = this.getSafetyGuide();
          this.showContactButton = false;
          break;
        case 'faq':
          this.guideTitle = '常见问题';
          this.guideSections = this.getFaqGuide();
          this.showContactButton = false;
          break;
        case 'service':
          this.guideTitle = '在线客服';
          this.guideSections = this.getServiceGuide();
          this.showContactButton = true;
          break;
        default:
          this.guideTitle = '使用指南';
          this.guideSections = this.getBeginnerGuide();
          this.showContactButton = false;
      }
    },
    
    // 获取新手指南内容
    getBeginnerGuide() {
      return [
        {
          title: '注册登录',
          icon: 'personadd',
          content: '首次使用需要使用手机号注册账号。登录后需要完成实名认证和基本信息填写，以便获得借款额度。',
          image: '/common/static/guide/register.png'
        },
        {
          title: '额度申请',
          icon: 'wallet',
          content: '完成个人信息认证后，系统会自动评估您的借款额度。额度大小取决于您的个人信息、信用状况等因素。',
          image: '/common/static/guide/credit.png'
        },
        {
          title: '借款申请',
          icon: 'auth',
          content: '在"借钱"页面，选择借款金额和期限，阅读并同意借款协议后，点击"申请借款"提交申请。申请审核通常在1-2个工作日内完成。',
          image: '/common/static/guide/borrow.png'
        },
        {
          title: '借款放款',
          icon: 'medal',
          content: '申请通过后，借款金额将在1个工作日内转入您的银行账户。请保持手机畅通，以便客服可能的电话核实。',
          image: '/common/static/guide/loan.png'
        },
        {
          title: '还款方式',
          icon: 'refresh',
          content: '在"还款"页面可以查看待还款项目。支持多种还款方式，包括支付宝、微信和银行卡还款。您可以选择按时还款或提前还款。',
          image: '/common/static/guide/repay.png'
        }
      ];
    },
    
    // 获取安全中心内容
    getSafetyGuide() {
      return [
        {
          title: '账户安全',
          icon: 'locked',
          content: '请使用复杂密码，并定期更换。不要在不安全的设备或网络上登录账户。切勿向任何人透露您的登录信息和验证码。',
          image: ''
        },
        {
          title: '交易安全',
          icon: 'shield',
          content: '所有的借款和还款交易都经过加密处理。请确保在官方渠道进行操作，谨防诈骗短信和电话。',
          image: ''
        },
        {
          title: '个人信息保护',
          icon: 'eye',
          content: '我们采用严格的数据加密和访问控制措施保护您的个人信息。除法律要求或获得您的授权外，不会向第三方披露您的个人信息。',
          image: ''
        },
        {
          title: '风险提示',
          icon: 'info',
          content: '借贷有风险，请根据自身经济状况合理借款。请务必按时还款，避免逾期对个人信用造成不良影响。',
          image: ''
        },
        {
          title: '防诈骗指南',
          icon: 'warning',
          content: '谨防冒充客服的诈骗电话和短信。我们不会以任何理由要求您支付预付费用或提供银行卡密码。如遇可疑情况，请立即联系客服。',
          image: ''
        }
      ];
    },
    
    // 获取常见问题内容
    getFaqGuide() {
      return [
        {
          title: '如何提高借款额度？',
          icon: 'help',
          content: '要提高借款额度，您可以：1. 保持良好的还款记录；2. 完善个人信息；3. 提高个人收入；4. 使用我们的服务时间越长，额度可能会相应提高。',
          image: ''
        },
        {
          title: '借款利率是如何计算的？',
          icon: 'help',
          content: '借款利率根据您的信用评分、借款金额和期限而定。具体利率在您申请借款时会显示，并在借款协议中明确说明。我们的利率符合相关法律法规规定。',
          image: ''
        },
        {
          title: '逾期会有什么后果？',
          icon: 'help',
          content: '逾期将产生逾期费用，且会对您的信用记录产生不良影响，可能导致未来借款额度降低或申请被拒。严重逾期可能会导致法律诉讼。',
          image: ''
        },
        {
          title: '如何提前还款？',
          icon: 'help',
          content: '在"还款"页面选择需要还款的借款项目，点击"立即还款"，选择还款方式并支付全部金额即可提前还款。提前还款不收取任何手续费。',
          image: ''
        },
        {
          title: '忘记密码怎么办？',
          icon: 'help',
          content: '在登录页面点击"忘记密码"，通过验证手机号和短信验证码后，可以重新设置密码。如遇到问题，请联系客服协助处理。',
          image: ''
        }
      ];
    },
    
    // 获取客服指南内容
    getServiceGuide() {
      return [
        {
          title: '在线客服',
          icon: 'headphones',
          content: '工作时间：周一至周五 9:00-18:00，法定节假日除外。您可以点击下方"联系客服"按钮，通过在线客服系统与我们联系。',
          image: ''
        },
        {
          title: '电话客服',
          icon: 'phone',
          content: '客服热线：400-888-8888\n工作时间：周一至周日 9:00-20:00',
          image: ''
        },
        {
          title: '常见问题',
          icon: 'help',
          content: '您可以在"常见问题"页面查找解答。我们收集了用户最常见的问题和解答，可能能够快速解决您的疑问。',
          image: ''
        },
        {
          title: '意见反馈',
          icon: 'compose',
          content: '如果您有任何建议或意见，欢迎向我们反馈。我们将认真对待每一条反馈，并不断改进我们的服务。',
          image: ''
        }
      ];
    },
    
    // 联系客服
    contactCustomerService() {
      // 模拟联系客服
      uni.showModal({
        title: '联系客服',
        content: '即将为您接通在线客服，是否继续？',
        success: function (res) {
          if (res.confirm) {
            uni.showToast({
              title: '客服系统连接中...',
              icon: 'none',
              duration: 2000
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
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.guide-header {
  background: linear-gradient(135deg, #33B19E, #29A28E);
  color: white;
  padding: 40rpx 30rpx;
  text-align: center;
}

.guide-title {
  font-size: 36rpx;
  font-weight: 600;
}

.guide-content {
  flex: 1;
  padding: 30rpx;
  background-color: #f7f7f7;
  overflow: hidden;
}

.content-scroll {
  height: 100%;
}

.section {
  background-color: #FFFFFF;
  border-radius: 20rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1px solid #f5f5f5;
}

.section-icon {
  width: 60rpx;
  height: 60rpx;
  background-color: #E5F7F2;
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 500;
  color: #333;
}

.section-content {
  padding: 30rpx;
}

.section-text {
  font-size: 28rpx;
  line-height: 1.8;
  color: #666;
  margin-bottom: 20rpx;
  display: block;
}

.section-image {
  width: 100%;
  border-radius: 10rpx;
  margin-top: 20rpx;
}

.guide-footer {
  padding: 30rpx;
  background-color: #FFFFFF;
  border-top: 1px solid #f1f1f1;
}

.contact-btn {
  width: 100%;
  height: 90rpx;
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
  border-radius: 45rpx;
  font-size: 32rpx;
  font-weight: 500;
}
</style> 