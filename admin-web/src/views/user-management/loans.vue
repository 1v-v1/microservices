<template>
  <div class="loan-management">
    <div class="page-header">
      <h2>贷款管理</h2>
      <p>管理系统中的所有贷款申请和记录</p>
    </div>
    
    <div class="search-section">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="贷款状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="还款中" value="repaying" />
            <el-option label="已结清" value="completed" />
            <el-option label="逾期" value="overdue" />
          </el-select>
        </el-form-item>
        <el-form-item label="信用等级">
          <el-select v-model="searchForm.creditLevel" placeholder="请选择信用等级" clearable>
            <el-option label="优秀 (700+)" value="excellent" />
            <el-option label="良好 (650-699)" value="good" />
            <el-option label="中等 (600-649)" value="fair" />
            <el-option label="及格 (550-599)" value="pass" />
            <el-option label="较差 (<550)" value="poor" />
          </el-select>
        </el-form-item>
        <el-form-item label="贷款金额">
          <el-input v-model="searchForm.minAmount" placeholder="最小金额" style="width: 120px" />
          <span style="margin: 0 8px">-</span>
          <el-input v-model="searchForm.maxAmount" placeholder="最大金额" style="width: 120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-section">
      <div class="stats-cards">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">¥ {{ formatAmount(totalLoans) }}</div>
                <div class="stat-label">总放款金额</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ pendingCount }}</div>
                <div class="stat-label">待审批</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ activeCount }}</div>
                <div class="stat-label">还款中</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ completedCount }}</div>
                <div class="stat-label">已结清</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <el-table 
        :data="paginatedLoanList" 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="loan_id" label="贷款ID" width="150">
          <template #default="{ row }">
            <el-tooltip :content="row.loan_id" placement="top">
              <span>{{ row.loan_id.slice(0, 8) }}...</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户信息" width="180">
          <template #default="{ row }">
            <div class="user-info-cell">
              <div class="username">{{ row.username }}</div>
              <div class="credit-info">
                <span class="credit-score" :class="getCreditClass(row.user_credit_score)">
                  {{ row.user_credit_score || '未知' }}分
                </span>
                <el-tag :type="getCreditTagType(row.user_credit_score)" size="small">
                  {{ getCreditLevel(row.user_credit_score) }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="loan_amount" label="贷款金额" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.loan_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="loan_term" label="贷款期限" width="100">
          <template #default="{ row }">
            {{ row.loan_term }}个月
          </template>
        </el-table-column>
        <el-table-column prop="interest_rate" label="利率" width="80">
          <template #default="{ row }">
            {{ parseFloat(row.interest_rate).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="monthly_payment" label="月还款额" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.monthly_payment) }}
          </template>
        </el-table-column>
        <el-table-column prop="remaining_amount" label="剩余金额" width="120">
          <template #default="{ row }">
            <span :class="{ 'remaining-amount': parseFloat(row.remaining_amount || 0) > 0 }">
              ¥{{ formatAmount(row.remaining_amount || 0) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="apply_date" label="申请时间" width="110" />
        <el-table-column prop="approve_date" label="批准时间" width="110">
          <template #default="{ row }">
            {{ row.approve_date || '未批准' }}
          </template>
        </el-table-column>
        <el-table-column prop="next_payment_date" label="下次还款" width="110">
          <template #default="{ row }">
            {{ row.next_payment_date && row.status === 'approved' ? row.next_payment_date : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">查看</el-button>
            <template v-if="row.status === 'pending'">
              <el-button 
                type="success" 
                size="small" 
                @click="handleApprove(row)"
                :disabled="approvalLoading"
              >
                批准
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="handleReject(row)"
                :disabled="approvalLoading"
              >
                拒绝
              </el-button>
              <el-button 
                type="info" 
                size="small" 
                @click="viewUserCredit(row)"
                title="查看信用详情"
              >
                信用分
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredLoanList.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 贷款详情对话框 -->
    <el-dialog v-model="dialogVisible" title="贷款详情" width="900px">
      <div v-if="currentLoan">
        <el-tabs>
          <el-tab-pane label="贷款信息" name="loan">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="贷款ID">{{ currentLoan.loan_id }}</el-descriptions-item>
              <el-descriptions-item label="用户名">{{ currentLoan.username }}</el-descriptions-item>
              <el-descriptions-item label="贷款金额">¥{{ formatAmount(currentLoan.loan_amount) }}</el-descriptions-item>
              <el-descriptions-item label="贷款期限">{{ currentLoan.loan_term }}天</el-descriptions-item>
              <el-descriptions-item label="利率">{{ parseFloat(currentLoan.interest_rate).toFixed(2) }}%</el-descriptions-item>
              <el-descriptions-item label="月还款额">¥{{ formatAmount(currentLoan.monthly_payment) }}</el-descriptions-item>
              <el-descriptions-item label="剩余金额">¥{{ formatAmount(currentLoan.remaining_amount || 0) }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentLoan.status)">
                  {{ getStatusText(currentLoan.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="申请时间">{{ currentLoan.apply_date }}</el-descriptions-item>
              <el-descriptions-item label="批准时间">{{ currentLoan.approve_date || '未批准' }}</el-descriptions-item>
              <el-descriptions-item label="下次还款日期">{{ currentLoan.next_payment_date || '-' }}</el-descriptions-item>
              <el-descriptions-item label="还款方式">{{ getRepayMethodText(currentLoan.repay_method) }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="用户信用信息" name="credit">
            <div class="credit-info-section">
              <div class="credit-summary">
                <div class="credit-score-display">
                  <div class="score-number" :class="getCreditClass(currentLoan.user_credit_score)">
                    {{ currentLoan.user_credit_score || '未知' }}
                  </div>
                  <div class="score-unit">分</div>
                  <div class="score-level">
                    <el-tag :type="getCreditTagType(currentLoan.user_credit_score)" size="large">
                      {{ getCreditLevel(currentLoan.user_credit_score) }}
                    </el-tag>
                  </div>
                </div>
                <div class="approval-advice">
                  <h4>审批建议</h4>
                  <div class="advice-content" v-if="currentLoan.user_credit_score">
                    <div v-if="currentLoan.user_credit_score >= 700" class="advice-item success">
                      <el-icon><CircleCheck /></el-icon>
                      <span>信用分达标，建议批准放款</span>
                    </div>
                    <div v-else-if="currentLoan.user_credit_score >= 600" class="advice-item warning">
                      <el-icon><Warning /></el-icon>
                      <span>信用分中等，建议谨慎审批，可适当降低额度</span>
                    </div>
                    <div v-else class="advice-item danger">
                      <el-icon><CircleClose /></el-icon>
                      <span>信用分较低，建议拒绝或要求提供担保</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="user-profile-summary" v-if="currentLoan.user_profile">
                <h4>用户资料完整度</h4>
                <el-progress 
                  :percentage="calculateProfileCompleteness(currentLoan.user_profile)" 
                  :color="getProgressColor(calculateProfileCompleteness(currentLoan.user_profile))"
                  style="margin-bottom: 20px;"
                />
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="真实姓名">
                    {{ currentLoan.user_profile?.realName || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="学历">
                    {{ currentLoan.user_profile?.education || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="工作状态">
                    {{ currentLoan.user_profile?.workStatus || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="收入水平">
                    {{ currentLoan.user_profile?.income || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="婚姻状况">
                    {{ currentLoan.user_profile?.maritalStatus || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="资产状况">
                    <span v-if="currentLoan.user_profile?.hasHouse === 'true' || currentLoan.user_profile?.hasCar === 'true'">
                      {{ currentLoan.user_profile?.hasHouse === 'true' ? '有房 ' : '' }}
                      {{ currentLoan.user_profile?.hasCar === 'true' ? '有车' : '' }}
                    </span>
                    <span v-else>无资产信息</span>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <!-- 待审批贷款的操作按钮 -->
        <div v-if="currentLoan.status === 'pending'" class="dialog-actions">
          <el-button type="success" @click="handleApprove(currentLoan)" :loading="approvalLoading">
            批准贷款
          </el-button>
          <el-button type="danger" @click="handleReject(currentLoan)" :loading="approvalLoading">
            拒绝贷款
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 用户信用详情对话框 -->
    <el-dialog v-model="creditDetailVisible" title="用户信用详情" width="800px">
      <div v-if="currentUserCredit" v-loading="creditDetailLoading">
        <!-- 信用详情内容与用户管理页面相同 -->
        <div class="user-credit-detail">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>基本信息</template>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="用户名">{{ currentUserCredit.username }}</el-descriptions-item>
                  <el-descriptions-item label="当前信用分">
                    <span :class="getCreditClass(currentUserCredit.current_score)">
                      {{ currentUserCredit.current_score }}分
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="信用等级">
                    <el-tag :type="getCreditTagType(currentUserCredit.current_score)">
                      {{ currentUserCredit.level }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>得分详情</template>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="基础分">{{ currentUserCredit.details?.base_score }}分</el-descriptions-item>
                  <el-descriptions-item label="基本信息">{{ currentUserCredit.details?.basic_info_score }}分</el-descriptions-item>
                  <el-descriptions-item label="学历加分">{{ currentUserCredit.details?.education_score }}分</el-descriptions-item>
                  <el-descriptions-item label="工作状态">{{ formatScoreWithSign(currentUserCredit.details?.work_score) }}分</el-descriptions-item>
                  <el-descriptions-item label="收入水平">{{ currentUserCredit.details?.income_score }}分</el-descriptions-item>
                  <el-descriptions-item label="资产状况">{{ currentUserCredit.details?.asset_score }}分</el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, Warning, CircleClose } from '@element-plus/icons-vue'
import axios from 'axios'

// 配置axios基础URL
const API_BASE_URL = 'http://localhost:8000'

// 响应式数据
const loading = ref(false)
const loanList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const currentLoan = ref(null)

// 搜索表单
const searchForm = reactive({
  username: '',
  status: '',
  minAmount: '',
  maxAmount: '',
  creditLevel: ''
})

// 新增响应式数据
const approvalLoading = ref(false)
const creditDetailVisible = ref(false)
const creditDetailLoading = ref(false)
const currentUserCredit = ref(null)

// 过滤后的贷款列表
const filteredLoanList = computed(() => {
  let filtered = loanList.value
  
  if (searchForm.username) {
    filtered = filtered.filter(loan => 
      loan.username?.toLowerCase().includes(searchForm.username.toLowerCase())
    )
  }
  
  if (searchForm.status) {
    filtered = filtered.filter(loan => loan.status === searchForm.status)
  }
  
  if (searchForm.minAmount) {
    const minAmount = parseFloat(searchForm.minAmount)
    if (!isNaN(minAmount)) {
      filtered = filtered.filter(loan => parseFloat(loan.loan_amount) >= minAmount)
    }
  }
  
  if (searchForm.maxAmount) {
    const maxAmount = parseFloat(searchForm.maxAmount)
    if (!isNaN(maxAmount)) {
      filtered = filtered.filter(loan => parseFloat(loan.loan_amount) <= maxAmount)
    }
  }
  
  if (searchForm.creditLevel) {
    filtered = filtered.filter(loan => {
      const score = parseInt(loan.user_credit_score || 700)
      switch (searchForm.creditLevel) {
        case 'excellent': return score >= 700
        case 'good': return score >= 650 && score < 700
        case 'fair': return score >= 600 && score < 650
        case 'pass': return score >= 550 && score < 600
        case 'poor': return score < 550
        default: return true
      }
    })
  }
  
  return filtered
})

// 分页后的贷款列表
const paginatedLoanList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLoanList.value.slice(start, end)
})

// 统计数据
const totalLoans = computed(() => {
  return loanList.value.reduce((sum, loan) => sum + parseFloat(loan.loan_amount || 0), 0)
})

const pendingCount = computed(() => {
  return loanList.value.filter(loan => loan.status === 'pending').length
})

const activeCount = computed(() => {
  return loanList.value.filter(loan => loan.status === 'approved' && parseFloat(loan.remaining_amount || 0) > 0).length
})

const completedCount = computed(() => {
  return loanList.value.filter(loan => loan.status === 'completed').length
})

// 状态相关函数
const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    approved: 'primary',
    rejected: 'danger',
    repaying: 'primary',
    completed: 'success',
    overdue: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    repaying: '还款中',
    completed: '已结清',
    overdue: '逾期'
  }
  return statusMap[status] || '未知'
}

// 信用分相关函数
const getCreditLevel = (score) => {
  const numScore = parseInt(score) || 700
  if (numScore >= 700) return '优秀'
  if (numScore >= 650) return '良好'
  if (numScore >= 600) return '中等'
  if (numScore >= 550) return '及格'
  return '较差'
}

const getCreditClass = (score) => {
  const numScore = parseInt(score) || 700
  if (numScore >= 700) return 'credit-excellent'
  if (numScore >= 650) return 'credit-good'
  if (numScore >= 600) return 'credit-fair'
  if (numScore >= 550) return 'credit-pass'
  return 'credit-poor'
}

const getCreditTagType = (score) => {
  const numScore = parseInt(score) || 700
  if (numScore >= 700) return 'success'
  if (numScore >= 650) return ''
  if (numScore >= 600) return 'warning'
  if (numScore >= 550) return 'info'
  return 'danger'
}

const getRepayMethodText = (method) => {
  const methodMap = {
    'equal-principal': '等额本金',
    'equal-installment': '等额本息'
  }
  return methodMap[method] || '未知'
}

const formatScoreWithSign = (score) => {
  const num = parseInt(score) || 0
  if (num > 0) return `+${num}`
  return num.toString()
}

// 格式化金额
const formatAmount = (amount) => {
  const num = parseFloat(amount) || 0
  return num.toLocaleString()
}

// 获取贷款列表
const getLoanList = async () => {
  loading.value = true
  try {
    const [loansResponse, usersResponse] = await Promise.all([
      axios.get(`${API_BASE_URL}/admin/loans`),
      axios.get(`${API_BASE_URL}/admin/users`)
    ])
    
    const loans = loansResponse.data.loans || []
    const users = usersResponse.data.users || []
    
    // 合并贷款和用户信息
    loanList.value = loans.map(loan => {
      const user = users.find(u => u.username === loan.username)
      return {
        ...loan,
        user_credit_score: user?.creditScore || 700,
        user_profile: user
      }
    })
    
    total.value = loanList.value.length
    ElMessage.success('贷款数据加载成功')
  } catch (error) {
    console.error('获取贷款列表失败:', error)
    ElMessage.error('获取贷款列表失败，请确保后端服务正在运行')
    loanList.value = []
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  // 过滤在计算属性中处理
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  currentPage.value = 1
}

// 查看详情
const handleView = (row) => {
  currentLoan.value = row
  dialogVisible.value = true
}

// 批准贷款
const handleApprove = async (row) => {
  const creditScore = row.user_credit_score || 700
  let confirmMessage = `确定要批准用户 ${row.username} 的贷款申请吗？\n\n`
  confirmMessage += `用户信用分：${creditScore}分 (${getCreditLevel(creditScore)})\n`
  confirmMessage += `贷款金额：¥${formatAmount(row.loan_amount)}\n`
  
  if (creditScore < 600) {
    confirmMessage += `\n⚠️ 注意：该用户信用分较低，请谨慎审批！`
  }
  
  try {
    await ElMessageBox.confirm(
      confirmMessage,
      '确认批准',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: creditScore >= 600 ? 'warning' : 'error'
      }
    )
    
    approvalLoading.value = true
    try {
      await axios.post(`${API_BASE_URL}/admin/loans/${row.loan_id}/approve`, {
        approved: true,
        remark: '管理员批准'
      })
      ElMessage.success('贷款申请已批准')
      dialogVisible.value = false // 关闭对话框
      getLoanList() // 重新获取贷款列表
    } catch (error) {
      console.error('批准贷款失败:', error)
      ElMessage.error('批准失败')
    } finally {
      approvalLoading.value = false
    }
  } catch {
    // 用户取消操作
  }
}

// 拒绝贷款
const handleReject = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝用户 ${row.username} 的贷款申请吗？`,
      '确认拒绝',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    approvalLoading.value = true
    try {
      await axios.post(`${API_BASE_URL}/admin/loans/${row.loan_id}/approve`, {
        approved: false,
        remark: '管理员拒绝'
      })
      ElMessage.success('贷款申请已拒绝')
      dialogVisible.value = false // 关闭对话框
      getLoanList() // 重新获取贷款列表
    } catch (error) {
      console.error('拒绝贷款失败:', error)
      ElMessage.error('拒绝失败')
    } finally {
      approvalLoading.value = false
    }
  } catch {
    // 用户取消操作
  }
}

// 查看用户信用详情
const viewUserCredit = async (row) => {
  creditDetailLoading.value = true
  creditDetailVisible.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/user/${row.username}/credit`)
    currentUserCredit.value = response.data.data
  } catch (error) {
    console.error('获取用户信用详情失败:', error)
    ElMessage.error('获取用户信用详情失败')
    creditDetailVisible.value = false
  } finally {
    creditDetailLoading.value = false
  }
}

// 计算用户资料完整度
const calculateProfileCompleteness = (profile) => {
  if (!profile) return 0
  
  const fields = [
    'realName', 'idCard', 'phone', 'education', 'workStatus', 
    'income', 'maritalStatus', 'contactName', 'contactPhone'
  ]
  
  const completedFields = fields.filter(field => profile[field] && profile[field].trim())
  return Math.round((completedFields.length / fields.length) * 100)
}

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}

// 页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

// 组件挂载时获取数据
onMounted(() => {
  getLoanList()
})
</script>

<style scoped>
.loan-management {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.search-section {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-form {
  margin: 0;
}

.table-section {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.remaining-amount {
  color: #e6a23c;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 用户信息单元格样式 */
.user-info-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.username {
  font-weight: 500;
  color: #303133;
}

.credit-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.credit-score {
  font-size: 12px;
  font-weight: 600;
}

.credit-excellent { color: #67C23A; }
.credit-good { color: #409EFF; }
.credit-fair { color: #E6A23C; }
.credit-pass { color: #909399; }
.credit-poor { color: #F56C6C; }

/* 信用详情页面样式 */
.credit-info-section {
  padding: 20px;
}

.credit-summary {
  display: flex;
  gap: 40px;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
}

.credit-score-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-number {
  font-size: 48px;
  font-weight: bold;
}

.score-unit {
  font-size: 16px;
  color: #909399;
}

.score-level {
  margin-left: 20px;
}

.approval-advice {
  flex: 1;
}

.approval-advice h4 {
  margin-bottom: 16px;
  color: #303133;
}

.advice-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.advice-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 14px;
}

.advice-item.success {
  background-color: #f0f9ff;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.advice-item.warning {
  background-color: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}

.advice-item.danger {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.user-profile-summary {
  margin-top: 30px;
}

.user-profile-summary h4 {
  margin-bottom: 16px;
  color: #303133;
}

.user-credit-detail {
  padding: 20px;
}

.dialog-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style> 