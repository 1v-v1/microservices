<template>
  <view class="container">
    <!-- 头部 -->
    <view class="header">
      <uni-nav-bar title="完善个人信息" left-icon="back" @click-left="goBack" />
    </view>

    <!-- 表单内容 -->
    <view class="form-container">
      <view class="form-header">
        <text class="form-title">为了提升您的借款额度</text>
        <text class="form-subtitle">请完善以下信息，提高信用评估</text>
      </view>

      <form @submit="submitForm">
        <!-- 基本信息 -->
        <view class="form-section">
          <view class="section-title">基本信息</view>
          
          <view class="form-item">
            <text class="label">真实姓名</text>
            <input 
              class="input" 
              v-model="formData.realName" 
              placeholder="请输入您的真实姓名"
              maxlength="20"
            />
          </view>

          <view class="form-item">
            <text class="label">身份证号</text>
            <input 
              class="input" 
              v-model="formData.idNumber" 
              placeholder="请输入身份证号码"
              maxlength="18"
            />
          </view>

          <view class="form-item">
            <text class="label">手机号码</text>
            <input 
              class="input" 
              v-model="formData.phone" 
              placeholder="请输入手机号码"
              type="number"
              maxlength="11"
            />
          </view>
        </view>

        <!-- 学历信息 -->
        <view class="form-section">
          <view class="section-title">学历信息</view>
          
          <view class="form-item">
            <text class="label">学历水平</text>
            <picker 
              @change="onEducationChange" 
              :value="formData.educationIndex" 
              :range="educationOptions"
            >
              <view class="picker">
                {{educationOptions[formData.educationIndex]}}
                <uni-icons type="right" size="14" color="#999"></uni-icons>
              </view>
            </picker>
          </view>

          <view class="form-item">
            <text class="label">毕业院校</text>
            <input 
              class="input" 
              v-model="formData.school" 
              placeholder="请输入毕业院校"
            />
          </view>
        </view>

        <!-- 婚姻状况 -->
        <view class="form-section">
          <view class="section-title">婚姻状况</view>
          
          <view class="form-item">
            <text class="label">婚姻状态</text>
            <picker 
              @change="onMaritalChange" 
              :value="formData.maritalIndex" 
              :range="maritalOptions"
            >
              <view class="picker">
                {{maritalOptions[formData.maritalIndex]}}
                <uni-icons type="right" size="14" color="#999"></uni-icons>
              </view>
            </picker>
          </view>
        </view>

        <!-- 工作信息 -->
        <view class="form-section">
          <view class="section-title">工作信息</view>
          
          <view class="form-item">
            <text class="label">工作状态</text>
            <picker 
              @change="onWorkStatusChange" 
              :value="formData.workStatusIndex" 
              :range="workStatusOptions"
            >
              <view class="picker">
                {{workStatusOptions[formData.workStatusIndex]}}
                <uni-icons type="right" size="14" color="#999"></uni-icons>
              </view>
            </picker>
          </view>

          <view class="form-item">
            <text class="label">工作单位</text>
            <input 
              class="input" 
              v-model="formData.company" 
              placeholder="请输入工作单位名称"
            />
          </view>

          <view class="form-item">
            <text class="label">职位</text>
            <input 
              class="input" 
              v-model="formData.position" 
              placeholder="请输入您的职位"
            />
          </view>

          <view class="form-item">
            <text class="label">月收入</text>
            <picker 
              @change="onIncomeChange" 
              :value="formData.incomeIndex" 
              :range="incomeOptions"
            >
              <view class="picker">
                {{incomeOptions[formData.incomeIndex]}}
                <uni-icons type="right" size="14" color="#999"></uni-icons>
              </view>
            </picker>
          </view>
        </view>

        <!-- 资产信息 -->
        <view class="form-section">
          <view class="section-title">资产信息</view>
          
          <view class="form-item">
            <text class="label">是否有房</text>
            <view class="radio-group">
              <label class="radio" @click="formData.hasHouse = true">
                <radio :checked="formData.hasHouse" color="#33B19E" />
                <text>有房产</text>
              </label>
              <label class="radio" @click="formData.hasHouse = false">
                <radio :checked="!formData.hasHouse" color="#33B19E" />
                <text>无房产</text>
              </label>
            </view>
          </view>

          <view class="form-item">
            <text class="label">是否有车</text>
            <view class="radio-group">
              <label class="radio" @click="formData.hasCar = true">
                <radio :checked="formData.hasCar" color="#33B19E" />
                <text>有车辆</text>
              </label>
              <label class="radio" @click="formData.hasCar = false">
                <radio :checked="!formData.hasCar" color="#33B19E" />
                <text>无车辆</text>
              </label>
            </view>
          </view>
        </view>

        <!-- 联系人信息 -->
        <view class="form-section">
          <view class="section-title">紧急联系人</view>
          
          <view class="form-item">
            <text class="label">联系人姓名</text>
            <input 
              class="input" 
              v-model="formData.contactName" 
              placeholder="请输入紧急联系人姓名"
            />
          </view>

          <view class="form-item">
            <text class="label">联系人电话</text>
            <input 
              class="input" 
              v-model="formData.contactPhone" 
              placeholder="请输入联系人电话"
              type="number"
              maxlength="11"
            />
          </view>

          <view class="form-item">
            <text class="label">与您的关系</text>
            <picker 
              @change="onRelationChange" 
              :value="formData.relationIndex" 
              :range="relationOptions"
            >
              <view class="picker">
                {{relationOptions[formData.relationIndex]}}
                <uni-icons type="right" size="14" color="#999"></uni-icons>
              </view>
            </picker>
          </view>
        </view>

        <!-- 提交按钮 -->
        <view class="submit-container">
          <button 
            class="submit-btn" 
            @click="submitForm"
            :disabled="!isFormValid"
            :class="{ 'disabled': !isFormValid }"
          >
            提交申请
          </button>
          <text class="submit-tips">提交后我们将在1-3个工作日内完成审核</text>
        </view>
      </form>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      formData: {
        realName: '',
        idNumber: '',
        phone: '',
        educationIndex: 0,
        school: '',
        maritalIndex: 0,
        workStatusIndex: 0,
        company: '',
        position: '',
        incomeIndex: 0,
        hasHouse: false,
        hasCar: false,
        contactName: '',
        contactPhone: '',
        relationIndex: 0
      },
      educationOptions: ['初中及以下', '高中/中专', '大专', '本科', '硕士', '博士'],
      maritalOptions: ['未婚', '已婚', '离异', '丧偶'],
      workStatusOptions: ['在职员工', '个体经营', '自由职业', '学生', '退休', '待业'],
      incomeOptions: ['3000以下', '3000-5000', '5000-8000', '8000-12000', '12000-20000', '20000以上'],
      relationOptions: ['父母', '配偶', '子女', '兄弟姐妹', '朋友', '同事', '其他']
    };
  },
  computed: {
    isFormValid() {
      return this.formData.realName.trim() !== '' &&
             this.formData.idNumber.trim() !== '' &&
             this.formData.phone.trim() !== '' &&
             this.formData.contactName.trim() !== '' &&
             this.formData.contactPhone.trim() !== '';
    }
  },
  methods: {
    goBack() {
      uni.navigateBack();
    },
    
    onEducationChange(e) {
      this.formData.educationIndex = e.detail.value;
    },
    
    onMaritalChange(e) {
      this.formData.maritalIndex = e.detail.value;
    },
    
    onWorkStatusChange(e) {
      this.formData.workStatusIndex = e.detail.value;
    },
    
    onIncomeChange(e) {
      this.formData.incomeIndex = e.detail.value;
    },
    
    onRelationChange(e) {
      this.formData.relationIndex = e.detail.value;
    },
    
    async submitForm() {
      if (!this.isFormValid) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        });
        return;
      }

      // 验证身份证格式
      if (!this.validateIdNumber(this.formData.idNumber)) {
        uni.showToast({
          title: '身份证格式不正确',
          icon: 'none'
        });
        return;
      }

      // 验证手机号格式
      if (!this.validatePhone(this.formData.phone)) {
        uni.showToast({
          title: '手机号格式不正确',
          icon: 'none'
        });
        return;
      }

      uni.showLoading({
        title: '提交中...'
      });

      try {
        // 准备提交数据
        const submitData = {
          realName: this.formData.realName,
          idNumber: this.formData.idNumber,
          phone: this.formData.phone,
          education: this.educationOptions[this.formData.educationIndex],
          school: this.formData.school,
          maritalStatus: this.maritalOptions[this.formData.maritalIndex],
          workStatus: this.workStatusOptions[this.formData.workStatusIndex],
          company: this.formData.company,
          position: this.formData.position,
          income: this.incomeOptions[this.formData.incomeIndex],
          hasHouse: this.formData.hasHouse,
          hasCar: this.formData.hasCar,
          contactName: this.formData.contactName,
          contactPhone: this.formData.contactPhone,
          relation: this.relationOptions[this.formData.relationIndex]
        };

        // 发送到后端
        const response = await new Promise((resolve, reject) => {
          uni.request({
            url: 'http://localhost:8000/api/user/update-info',
            method: 'POST',
            data: submitData,
            header: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + uni.getStorageSync('token')
            },
            success: (res) => {
              console.log('API响应:', res);
              resolve(res);
            },
            fail: (err) => {
              console.error('请求失败:', err);
              reject(err);
            }
          });
        });

        uni.hideLoading();

        if (response.statusCode === 200 && response.data && response.data.success) {
          uni.showToast({
            title: '提交成功',
            icon: 'success'
          });
          
          setTimeout(() => {
            uni.navigateBack();
          }, 1500);
        } else {
          uni.showToast({
            title: response.data?.message || '提交失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('提交失败:', error);
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    },
    
    validateIdNumber(idNumber) {
      const pattern = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;
      return pattern.test(idNumber);
    },
    
    validatePhone(phone) {
      const pattern = /^1[3-9]\d{9}$/;
      return pattern.test(phone);
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  background-color: #33B19E;
  color: white;
}

.form-container {
  padding: 20rpx;
}

.form-header {
  background-color: white;
  border-radius: 20rpx;
  padding: 40rpx;
  margin-bottom: 20rpx;
  text-align: center;
}

.form-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.form-subtitle {
  font-size: 28rpx;
  color: #666;
  display: block;
}

.form-section {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #f0f0f0;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-item:last-child {
  margin-bottom: 0;
}

.label {
  font-size: 30rpx;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 88rpx;
  background-color: #f8f8f8;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 30rpx;
  border: 2rpx solid transparent;
  box-sizing: border-box;
}

.input:focus {
  border-color: #33B19E;
  background-color: white;
}

.picker {
  width: 100%;
  height: 88rpx;
  background-color: #f8f8f8;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 30rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 2rpx solid transparent;
  box-sizing: border-box;
}

.picker:active {
  border-color: #33B19E;
  background-color: white;
}

.radio-group {
  display: flex;
  gap: 40rpx;
}

.radio {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 30rpx;
  color: #333;
}

.submit-container {
  padding: 40rpx 20rpx;
  text-align: center;
}

.submit-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(to right, #33B19E, #29A28E);
  color: white;
  border: none;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: 600;
  margin-bottom: 20rpx;
}

.submit-btn.disabled {
  background: #ccc;
  color: #999;
}

.submit-tips {
  font-size: 24rpx;
  color: #999;
  display: block;
}
</style> 