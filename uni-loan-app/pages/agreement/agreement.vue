<template>
  <view class="container">
    <view class="agreement-header">
      <text class="agreement-title">{{agreementTitle}}</text>
    </view>
    
    <view class="agreement-content">
      <scroll-view scroll-y class="content-scroll">
        <rich-text :nodes="agreementContent"></rich-text>
      </scroll-view>
    </view>
    
    <view class="agreement-footer" v-if="showFooter">
      <button class="confirm-btn" @click="confirmAgreement">我已阅读并同意</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      agreementType: '', // 协议类型
      agreementTitle: '协议详情', // 协议标题
      showFooter: false, // 是否显示底部确认按钮
      agreementContent: '' // 协议内容
    };
  },
  onLoad(options) {
    // 获取路由参数
    if (options.type) {
      this.agreementType = options.type;
      
      // 设置标题
      if (options.title) {
        this.agreementTitle = options.title;
      } else {
        this.setTitleByType();
      }
      
      // 设置协议内容
      this.loadAgreementContent();
    }
    
    // 是否显示底部确认按钮
    this.showFooter = options.showFooter === 'true';
  },
  methods: {
    // 根据类型设置标题
    setTitleByType() {
      switch(this.agreementType) {
        case 'service':
          this.agreementTitle = '服务协议';
          break;
        case 'privacy':
          this.agreementTitle = '隐私政策';
          break;
        case 'loan':
          this.agreementTitle = '借款协议';
          break;
        case 'repayment':
          this.agreementTitle = '还款协议';
          break;
        default:
          this.agreementTitle = '协议详情';
      }
    },
    
    // 加载协议内容
    loadAgreementContent() {
      let content = '';
      
      switch(this.agreementType) {
        case 'service':
          content = this.getServiceAgreement();
          break;
        case 'privacy':
          content = this.getPrivacyPolicy();
          break;
        case 'loan':
          content = this.getLoanAgreement();
          break;
        case 'repayment':
          content = this.getRepaymentAgreement();
          break;
        default:
          content = '<p>未找到相关协议内容</p>';
      }
      
      this.agreementContent = content;
    },
    
    // 获取服务协议内容
    getServiceAgreement() {
      return `
        <h3>服务协议</h3>
        <p>欢迎使用我们的服务。请仔细阅读以下条款，使用我们的服务即表示您同意这些条款。</p>
        
        <h4>1. 服务内容</h4>
        <p>我们提供个人借贷信息中介服务，帮助您获得个人贷款。我们不直接提供贷款，仅作为信息服务平台。</p>
        
        <h4>2. 用户资格</h4>
        <p>您确认自己年满18周岁且具有完全民事行为能力，能够独立承担民事责任。</p>
        
        <h4>3. 信息真实性</h4>
        <p>您承诺提供真实、准确、完整的个人信息，并保证及时更新相关信息。如提供虚假信息，我们有权终止服务。</p>
        
        <h4>4. 服务变更与终止</h4>
        <p>我们可能会不时地更改服务内容，或者终止服务。无论出于何种原因终止服务，我们将提前通知您。</p>
        
        <h4>5. 知识产权</h4>
        <p>我们的服务包含的所有内容均受版权、商标和其他法律保护。未经我们许可，不得使用这些内容。</p>
        
        <h4>6. 免责声明</h4>
        <p>我们不对因使用我们的服务而产生的任何直接、间接、附带、特殊或后果性损害承担责任。</p>
        
        <h4>7. 适用法律</h4>
        <p>本协议受中华人民共和国法律管辖并按其解释。</p>
      `;
    },
    
    // 获取隐私政策内容
    getPrivacyPolicy() {
      return `
        <h3>隐私政策</h3>
        <p>我们非常重视您的隐私保护，本隐私政策说明我们如何收集、使用、披露、处理和保护您的信息。</p>
        
        <h4>1. 信息收集</h4>
        <p>我们可能收集您的个人信息，包括但不限于姓名、联系方式、身份证号码、银行账户、职业信息等。</p>
        
        <h4>2. 信息使用</h4>
        <p>我们使用收集的信息来提供、维护、保护和改进我们的服务，开发新的服务，并保护我们和用户。</p>
        
        <h4>3. 信息共享</h4>
        <p>除非得到您的同意，或法律要求，或以下情况，我们不会与第三方分享您的个人信息：
          <br>- 与合作的金融机构共享，用于贷款审批和发放
          <br>- 与提供技术支持的服务商共享必要信息
        </p>
        
        <h4>4. 信息安全</h4>
        <p>我们采取合理的安全措施来保护您的个人信息免遭未经授权的访问、使用或披露。</p>
        
        <h4>5. 您的权利</h4>
        <p>您有权访问、更正您的个人信息，并要求删除您的账户。</p>
        
        <h4>6. 政策更新</h4>
        <p>我们可能会不时更新本隐私政策。当我们更新隐私政策时，我们会在应用中通知您。</p>
      `;
    },
    
    // 获取借款协议内容
    getLoanAgreement() {
      return `
        <h3>借款协议</h3>
        <p>本协议由借款人（以下简称"您"）与借款服务提供方（以下简称"我们"）共同签署。</p>
        
        <h4>1. 借款内容</h4>
        <p>借款金额、期限、利率、还款方式等具体内容以借款申请页面显示及最终审批结果为准。</p>
        
        <h4>2. 借款用途</h4>
        <p>您承诺将借款用于个人消费，不得用于非法活动或投资股票、期货等风险投资。</p>
        
        <h4>3. 还款责任</h4>
        <p>您应按照约定的还款计划按时足额还款。如无法按时还款，应提前联系我们协商处理。</p>
        
        <h4>4. 逾期责任</h4>
        <p>如您未按时还款，将产生逾期费用，并可能影响您的信用记录。具体逾期费率以借款页面显示为准。</p>
        
        <h4>5. 提前还款</h4>
        <p>您可以提前归还全部借款，无需支付额外费用。</p>
        
        <h4>6. 通知方式</h4>
        <p>与借款相关的通知将通过短信、电子邮件或应用内消息发送给您。</p>
        
        <h4>7. 争议解决</h4>
        <p>因本协议引起的争议，双方应协商解决；协商不成的，提交借款服务提供方所在地有管辖权的人民法院解决。</p>
      `;
    },
    
    // 获取还款协议内容
    getRepaymentAgreement() {
      return `
        <h3>还款协议</h3>
        <p>本协议规定了您的还款义务和权利，请仔细阅读。</p>
        
        <h4>1. 还款方式</h4>
        <p>您可以通过以下方式进行还款：
          <br>- 支付宝支付
          <br>- 微信支付
          <br>- 银行卡支付
        </p>
        
        <h4>2. 还款计划</h4>
        <p>您应当按照借款时确定的还款计划按时足额还款。还款计划可在应用"我的借款"中查看。</p>
        
        <h4>3. 还款日</h4>
        <p>每月的还款日为借款发放日的对应日。如当月无对应日，则以当月最后一日为还款日。</p>
        
        <h4>4. 提前还款</h4>
        <p>您可以随时提前归还全部借款，无需支付额外费用。提前还款将减少您的利息支出。</p>
        
        <h4>5. 还款顺序</h4>
        <p>您的还款将按照以下顺序清偿：逾期费用、逾期利息、正常利息、本金。</p>
        
        <h4>6. 逾期处理</h4>
        <p>如您未能按时还款，将产生逾期费用，并会影响您的信用记录。逾期严重的，我们有权采取法律手段追讨欠款。</p>
        
        <h4>7. 还款通知</h4>
        <p>我们会在还款日前通过短信、电子邮件或应用内消息提醒您按时还款。</p>
      `;
    },
    
    // 确认协议
    confirmAgreement() {
      const pages = getCurrentPages();
      const prevPage = pages[pages.length - 2]; // 获取上一个页面
      
      // 通知上一个页面用户已同意协议
      if (prevPage && prevPage.$vm) {
        prevPage.$vm.agreementConfirmed && prevPage.$vm.agreementConfirmed(this.agreementType);
      }
      
      // 返回上一页
      uni.navigateBack();
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

.agreement-header {
  background-color: #FFFFFF;
  padding: 40rpx 30rpx;
  border-bottom: 1px solid #f1f1f1;
  text-align: center;
}

.agreement-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.agreement-content {
  flex: 1;
  padding: 30rpx;
  background-color: #FFFFFF;
  overflow: hidden;
}

.content-scroll {
  height: 100%;
}

.agreement-footer {
  padding: 30rpx;
  background-color: #FFFFFF;
  border-top: 1px solid #f1f1f1;
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
}

/* 富文本样式 */
rich-text {
  font-size: 28rpx;
  line-height: 1.8;
  color: #333;
}

rich-text h3 {
  font-size: 36rpx;
  font-weight: 600;
  margin: 40rpx 0 30rpx;
  color: #333;
}

rich-text h4 {
  font-size: 32rpx;
  font-weight: 500;
  margin: 30rpx 0 20rpx;
  color: #333;
}

rich-text p {
  margin-bottom: 20rpx;
  color: #666;
}
</style> 