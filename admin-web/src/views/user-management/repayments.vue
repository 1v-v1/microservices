<template>
  <div class="repayment-management">
    <div class="page-header">
      <h2>还款管理</h2>
      <p>管理系统中的所有还款记录</p>
    </div>

    <div class="search-section">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="贷款ID">
          <el-input v-model="searchForm.loanId" placeholder="请输入贷款ID" clearable />
        </el-form-item>
        <el-form-item label="还款状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="已完成" value="completed" />
            <el-option label="处理中" value="pending" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="还款日期">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 300px"
          />
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
                <div class="stat-value">¥ {{ formatAmount(totalRepaymentAmount) }}</div>
                <div class="stat-label">总还款金额</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ completedCount }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ pendingCount }}</div>
                <div class="stat-label">处理中</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ failedCount }}</div>
                <div class="stat-label">失败</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <el-table 
        :data="paginatedRepaymentList" 
        v-loading="loading" 
        style="width: 100%" 
        border
      >
        <el-table-column prop="repayment_id" label="还款ID" width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.repayment_id" placement="top">
              <span>{{ row.repayment_id.slice(0, 8) }}...</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="loan_id" label="贷款ID" width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.loan_id" placement="top">
              <span>{{ row.loan_id.slice(0, 8) }}...</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="amount" label="还款金额" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="还款日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getRepaymentStatusType(row.status)">
              {{ getRepaymentStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredRepaymentList.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 还款详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="还款详情" width="600px">
      <div v-if="currentRepayment">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="还款ID" :span="2">{{ currentRepayment.repayment_id }}</el-descriptions-item>
          <el-descriptions-item label="贷款ID" :span="2">{{ currentRepayment.loan_id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ currentRepayment.username }}</el-descriptions-item>
          <el-descriptions-item label="还款金额">¥{{ formatAmount(currentRepayment.amount) }}</el-descriptions-item>
          <el-descriptions-item label="还款日期">{{ currentRepayment.payment_date }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getRepaymentStatusType(currentRepayment.status)">
              {{ getRepaymentStatusText(currentRepayment.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 配置axios基础URL
const API_BASE_URL = 'http://localhost:8000'

// 响应式数据
const loading = ref(false)
const repaymentList = ref([])
const currentPage = ref(1)
const pageSize = ref(10) // 每页10条数据
const detailDialogVisible = ref(false)
const currentRepayment = ref(null)

// 搜索表单
const searchForm = reactive({
  username: '',
  loanId: '',
  status: '',
  dateRange: null
})

// 过滤后的还款列表
const filteredRepaymentList = computed(() => {
  let filtered = repaymentList.value
  
  if (searchForm.username) {
    filtered = filtered.filter(repayment => 
      repayment.username?.toLowerCase().includes(searchForm.username.toLowerCase())
    )
  }
  
  if (searchForm.loanId) {
    filtered = filtered.filter(repayment => 
      repayment.loan_id?.toLowerCase().includes(searchForm.loanId.toLowerCase())
    )
  }
  
  if (searchForm.status) {
    filtered = filtered.filter(repayment => repayment.status === searchForm.status)
  }
  
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    const startDate = new Date(searchForm.dateRange[0])
    const endDate = new Date(searchForm.dateRange[1])
    filtered = filtered.filter(repayment => {
      const paymentDate = new Date(repayment.payment_date)
      return paymentDate >= startDate && paymentDate <= endDate
    })
  }
  
  return filtered
})

// 分页后的还款列表
const paginatedRepaymentList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRepaymentList.value.slice(start, end)
})

// 统计数据
const totalRepaymentAmount = computed(() => {
  return repaymentList.value.reduce((sum, repayment) => sum + parseFloat(repayment.amount || 0), 0)
})

const completedCount = computed(() => {
  return repaymentList.value.filter(repayment => repayment.status === 'completed').length
})

const pendingCount = computed(() => {
  return repaymentList.value.filter(repayment => repayment.status === 'pending').length
})

const failedCount = computed(() => {
  return repaymentList.value.filter(repayment => repayment.status === 'failed').length
})

// 获取还款列表
const fetchRepayments = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/repayments`)
    repaymentList.value = response.data.repayments || []
    ElMessage.success('还款数据加载成功')
  } catch (error) {
    console.error('获取还款列表失败:', error)
    ElMessage.error('获取还款列表失败，请确保后端服务正在运行')
    repaymentList.value = []
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
    if (key === 'dateRange') {
      searchForm[key] = null
    } else {
      searchForm[key] = ''
    }
  })
  currentPage.value = 1
}

// 查看还款详情
const handleViewDetail = (repayment) => {
  currentRepayment.value = repayment
  detailDialogVisible.value = true
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

// 格式化金额
const formatAmount = (amount) => {
  const num = parseFloat(amount) || 0
  return num.toLocaleString()
}

// 获取还款状态类型
const getRepaymentStatusType = (status) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'pending':
      return 'warning'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取还款状态文本
const getRepaymentStatusText = (status) => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'pending':
      return '处理中'
    case 'failed':
      return '失败'
    default:
      return '未知'
  }
}

onMounted(() => {
  fetchRepayments()
})
</script>

<style scoped>
.repayment-management {
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 