<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <p>管理系统中的所有用户信息</p>
    </div>
    
    <div class="search-section">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="searchForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="资料状态">
          <el-select v-model="searchForm.profileStatus" placeholder="请选择状态" clearable>
            <el-option label="已完善" value="true" />
            <el-option label="未完善" value="false" />
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
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-section">
      <div class="table-header">
        <el-button type="danger" @click="handleBatchDelete" :disabled="!selectedUsers.length">批量删除</el-button>
        <div class="user-stats">
          <el-tag>总用户数: {{ total }}</el-tag>
          <el-tag type="success">已完善资料: {{ completedProfileCount }}</el-tag>
          <el-tag type="warning">未完善资料: {{ incompleteProfileCount }}</el-tag>
          <el-tag type="success">优秀信用: {{ excellentCreditCount }}</el-tag>
          <el-tag type="danger">不及格信用: {{ poorCreditCount }}</el-tag>
          <el-tag type="info">平均信用分: {{ averageCreditScore }}</el-tag>
        </div>
      </div>
      
      <el-table 
        :data="paginatedUserList" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="realName" label="真实姓名" width="100">
          <template #default="{ row }">
            {{ row.realName || '未填写' }}
          </template>
        </el-table-column>
        <el-table-column prop="idCard" label="身份证" width="150">
          <template #default="{ row }">
            {{ row.idCard ? maskIdCard(row.idCard) : '未填写' }}
          </template>
        </el-table-column>
        <el-table-column prop="bankName" label="银行" width="120">
          <template #default="{ row }">
            {{ row.bankName || '未绑定' }}
          </template>
        </el-table-column>
        <el-table-column prop="creditScore" label="信用分" width="120" align="center">
          <template #default="{ row }">
            <div class="credit-score-cell">
              <div class="score-value" :class="getCreditScoreClass(row.creditScore)">
                {{ row.creditScore || 700 }}
              </div>
              <el-tag :type="getCreditScoreType(row.creditScore)" size="small">
                {{ getCreditLevel(row.creditScore) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="monthlyIncome" label="月收入" width="100">
          <template #default="{ row }">
            {{ row.monthlyIncome ? `¥${formatAmount(row.monthlyIncome)}` : '未填写' }}
          </template>
        </el-table-column>
        <el-table-column prop="totalBorrowed" label="总借款" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.totalBorrowed || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="pendingRepay" label="待还款" width="120">
          <template #default="{ row }">
            <span :class="{ 'overdue-amount': parseFloat(row.pendingRepay || 0) > 0 }">
              ¥{{ formatAmount(row.pendingRepay || 0) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="isProfileCompleted" label="资料状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isProfileCompleted === 'true' ? 'success' : 'warning'">
              {{ row.isProfileCompleted === 'true' ? '已完善' : '未完善' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <!-- 桌面端布局 -->
              <div class="desktop-actions">
                <el-button-group>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="handleView(row)"
                    :icon="View"
                    title="查看详情"
                  >
                    查看
                  </el-button>
                  <el-button 
                    type="success" 
                    size="small" 
                    @click="handleEdit(row)"
                    :icon="Edit"
                    title="编辑用户"
                  >
                    编辑
                  </el-button>
                </el-button-group>
                
                <!-- 更多操作下拉菜单 -->
                <el-dropdown trigger="click" @command="handleCommand($event, row)">
                  <el-button 
                    size="small" 
                    type="info"
                    :icon="More"
                    title="更多操作"
                  >
                    更多
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="recalculate" :icon="Refresh">
                        <span>重算信用分</span>
                      </el-dropdown-item>
                      <el-dropdown-item divided command="delete" class="danger-item">
                        <el-icon color="#f56c6c"><Delete /></el-icon>
                        <span style="color: #f56c6c;">删除用户</span>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              
              <!-- 移动端布局 -->
              <div class="mobile-actions">
                <el-dropdown trigger="click" @command="handleCommand($event, row)" placement="bottom-end">
                  <el-button 
                    size="small" 
                    type="primary"
                    :icon="More"
                    circle
                    title="操作菜单"
                  />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="view" :icon="View">
                        <span>查看详情</span>
                      </el-dropdown-item>
                      <el-dropdown-item command="edit" :icon="Edit">
                        <span>编辑信息</span>
                      </el-dropdown-item>
                      <el-dropdown-item command="recalculate" :icon="Refresh">
                        <span>重算信用分</span>
                      </el-dropdown-item>
                      <el-dropdown-item divided command="delete" class="danger-item">
                        <el-icon color="#f56c6c"><Delete /></el-icon>
                        <span style="color: #f56c6c;">删除用户</span>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredUserList.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="dialogVisible" title="用户详情" width="800px">
      <div v-if="currentUser">
        <el-tabs>
          <el-tab-pane label="基本信息" name="basic">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
              <el-descriptions-item label="真实姓名">{{ currentUser.realName || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="手机号">{{ currentUser.phone || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="身份证">{{ currentUser.idCard || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="银行卡">{{ currentUser.bankCard || '未绑定' }}</el-descriptions-item>
              <el-descriptions-item label="开户银行">{{ currentUser.bankName || '未绑定' }}</el-descriptions-item>
              <el-descriptions-item label="月收入">{{ currentUser.monthlyIncome ? `¥${formatAmount(currentUser.monthlyIncome)}` : '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="信用分">{{ currentUser.creditScore || 700 }}</el-descriptions-item>
              <el-descriptions-item label="贷款额度">¥{{ formatAmount(currentUser.loanLimit || 50000) }}</el-descriptions-item>
              <el-descriptions-item label="总借款">¥{{ formatAmount(currentUser.totalBorrowed || 0) }}</el-descriptions-item>
              <el-descriptions-item label="待还款">¥{{ formatAmount(currentUser.pendingRepay || 0) }}</el-descriptions-item>
              <el-descriptions-item label="资料状态">
                <el-tag :type="currentUser.isProfileCompleted === 'true' ? 'success' : 'warning'">
                  {{ currentUser.isProfileCompleted === 'true' ? '已完善' : '未完善' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="详细信息" name="detailed">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="学历">{{ currentUser.education || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="毕业院校">{{ currentUser.school || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="婚姻状况">{{ currentUser.maritalStatus || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="工作状态">{{ currentUser.workStatus || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="工作单位">{{ currentUser.company || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="职位">{{ currentUser.position || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="收入范围">{{ currentUser.income || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="是否有房">
                <el-tag :type="currentUser.hasHouse === 'true' ? 'success' : 'info'">
                  {{ currentUser.hasHouse === 'true' ? '有房产' : currentUser.hasHouse === 'false' ? '无房产' : '未填写' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="是否有车">
                <el-tag :type="currentUser.hasCar === 'true' ? 'success' : 'info'">
                  {{ currentUser.hasCar === 'true' ? '有车辆' : currentUser.hasCar === 'false' ? '无车辆' : '未填写' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="联系人信息" name="contact">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="联系人姓名">{{ currentUser.contactName || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="联系人电话">{{ currentUser.contactPhone || '未填写' }}</el-descriptions-item>
              <el-descriptions-item label="与用户关系">{{ currentUser.relation || '未填写' }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="信用分详情" name="credit">
            <div class="credit-detail">
              <div class="credit-header">
                <div class="current-score">
                  <div class="score-number" :class="getCreditScoreClass(currentUser.creditScore)">
                    {{ currentUser.creditScore || 700 }}
                  </div>
                  <div class="score-unit">分</div>
                </div>
                <div class="score-info">
                  <div class="score-level">
                    <el-tag :type="getCreditScoreType(currentUser.creditScore)" size="large">
                      {{ getCreditLevel(currentUser.creditScore) }}
                    </el-tag>
                  </div>
                  <div class="score-desc">
                    {{ getCreditDescription(currentUser.creditScore) }}
                  </div>
                </div>
                <div class="score-actions">
                  <el-button type="primary" @click="recalculateCurrentUserCredit" :loading="recalculatingCurrentUser">
                    重新计算信用分
                  </el-button>
                  <el-button type="info" @click="viewCreditRules">查看计算规则</el-button>
                </div>
              </div>
              
              <el-divider>信用分构成</el-divider>
              
              <div v-if="currentUserCreditDetail" class="credit-breakdown">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-card title="得分详情" shadow="never">
                      <el-descriptions :column="1" border>
                        <el-descriptions-item label="基础分">{{ currentUserCreditDetail.details.base_score }}分</el-descriptions-item>
                        <el-descriptions-item label="基本信息">{{ currentUserCreditDetail.details.basic_info_score }}分</el-descriptions-item>
                        <el-descriptions-item label="学历加分">{{ currentUserCreditDetail.details.education_score }}分</el-descriptions-item>
                        <el-descriptions-item label="婚姻状况">{{ formatScoreWithSign(currentUserCreditDetail.details.marital_score) }}分</el-descriptions-item>
                        <el-descriptions-item label="工作状态">{{ formatScoreWithSign(currentUserCreditDetail.details.work_score) }}分</el-descriptions-item>
                        <el-descriptions-item label="收入水平">{{ currentUserCreditDetail.details.income_score }}分</el-descriptions-item>
                        <el-descriptions-item label="资产状况">{{ currentUserCreditDetail.details.asset_score }}分</el-descriptions-item>
                        <el-descriptions-item label="联系人信息">{{ currentUserCreditDetail.details.contact_score }}分</el-descriptions-item>
                      </el-descriptions>
                    </el-card>
                  </el-col>
                  <el-col :span="12">
                    <el-card title="信息完整度评估" shadow="never">
                      <div class="info-completeness">
                        <div class="completeness-item" :class="{ 'complete': currentUser.education }">
                          <el-icon><Document /></el-icon>
                          <span>学历信息</span>
                          <el-tag :type="currentUser.education ? 'success' : 'info'" size="small">
                            {{ currentUser.education ? '已填写' : '未填写' }}
                          </el-tag>
                        </div>
                        <div class="completeness-item" :class="{ 'complete': currentUser.workStatus }">
                          <el-icon><Briefcase /></el-icon>
                          <span>工作信息</span>
                          <el-tag :type="currentUser.workStatus ? 'success' : 'info'" size="small">
                            {{ currentUser.workStatus ? '已填写' : '未填写' }}
                          </el-tag>
                        </div>
                        <div class="completeness-item" :class="{ 'complete': currentUser.income }">
                          <el-icon><Money /></el-icon>
                          <span>收入信息</span>
                          <el-tag :type="currentUser.income ? 'success' : 'info'" size="small">
                            {{ currentUser.income ? '已填写' : '未填写' }}
                          </el-tag>
                        </div>
                        <div class="completeness-item" :class="{ 'complete': currentUser.hasHouse === 'true' || currentUser.hasCar === 'true' }">
                          <el-icon><House /></el-icon>
                          <span>资产信息</span>
                          <el-tag :type="(currentUser.hasHouse === 'true' || currentUser.hasCar === 'true') ? 'success' : 'info'" size="small">
                            {{ (currentUser.hasHouse === 'true' || currentUser.hasCar === 'true') ? '已填写' : '未填写' }}
                          </el-tag>
                        </div>
                        <div class="completeness-item" :class="{ 'complete': currentUser.contactName && currentUser.contactPhone }">
                          <el-icon><Phone /></el-icon>
                          <span>联系人信息</span>
                          <el-tag :type="(currentUser.contactName && currentUser.contactPhone) ? 'success' : 'info'" size="small">
                            {{ (currentUser.contactName && currentUser.contactPhone) ? '已填写' : '未填写' }}
                          </el-tag>
                        </div>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
              
              <div v-else class="no-credit-detail">
                <el-empty description="点击重新计算获取详细信用分析" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 信用分计算规则对话框 -->
    <el-dialog v-model="creditRulesVisible" title="信用分计算规则" width="900px">
      <div v-if="creditRules" class="credit-rules-content">
        <el-alert
          title="信用分计算说明"
          type="info"
          description="信用分基于用户的个人信息进行综合评估，满分750分，及格分550分。分数越高表示用户信用状况越良好。"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card title="学历加分规则" shadow="never">
              <el-table :data="formatRuleData(creditRules.rules.education.options)" size="small">
                <el-table-column prop="option" label="学历水平" />
                <el-table-column prop="score" label="加分" />
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card title="婚姻状况规则" shadow="never">
              <el-table :data="formatRuleData(creditRules.rules.maritalStatus.options)" size="small">
                <el-table-column prop="option" label="婚姻状态" />
                <el-table-column prop="score" label="加分" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card title="工作状态规则" shadow="never">
              <el-table :data="formatRuleData(creditRules.rules.workStatus.options)" size="small">
                <el-table-column prop="option" label="工作状态" />
                <el-table-column prop="score" label="加分" />
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card title="收入水平规则" shadow="never">
              <el-table :data="formatRuleData(creditRules.rules.income.options)" size="small">
                <el-table-column prop="option" label="收入范围" />
                <el-table-column prop="score" label="加分" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card title="资产状况规则" shadow="never">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="有房产">+{{ creditRules.rules.assets.house_score }}分</el-descriptions-item>
                <el-descriptions-item label="有车辆">+{{ creditRules.rules.assets.car_score }}分</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card title="信用等级划分" shadow="never">
              <el-table :data="formatLevelData(creditRules.levels)" size="small">
                <el-table-column prop="level" label="等级" />
                <el-table-column prop="range" label="分数范围" />
                <el-table-column prop="color" label="标识">
                  <template #default="{ row }">
                    <el-tag :type="row.tagType">{{ row.level }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Briefcase, Money, House, Phone, View, Edit, Refresh, More, Delete, ArrowDown } from '@element-plus/icons-vue'
import axios from 'axios'

// 配置axios基础URL
const API_BASE_URL = 'http://localhost:8000'

// 响应式数据
const loading = ref(false)
const userList = ref([])
const selectedUsers = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const currentUser = ref(null)
const creditRulesVisible = ref(false)
const creditRules = ref(null)
const currentUserCreditDetail = ref(null)
const recalculatingUsers = ref([])
const recalculatingCurrentUser = ref(false)

// 搜索表单
const searchForm = reactive({
  username: '',
  phone: '',
  profileStatus: '',
  creditLevel: ''
})

// 计算属性
const completedProfileCount = computed(() => {
  return userList.value.filter(user => user.isProfileCompleted === 'true').length
})

const incompleteProfileCount = computed(() => {
  return userList.value.filter(user => user.isProfileCompleted !== 'true').length
})

const excellentCreditCount = computed(() => {
  return userList.value.filter(user => {
    const score = parseInt(user.creditScore || 700)
    return score >= 700
  }).length
})

const poorCreditCount = computed(() => {
  return userList.value.filter(user => {
    const score = parseInt(user.creditScore || 700)
    return score < 550
  }).length
})

const averageCreditScore = computed(() => {
  if (userList.value.length === 0) return 0
  const total = userList.value.reduce((sum, user) => sum + parseInt(user.creditScore || 700), 0)
  return Math.round(total / userList.value.length)
})

// 过滤后的用户列表
const filteredUserList = computed(() => {
  let filtered = userList.value
  
  if (searchForm.username) {
    filtered = filtered.filter(user => 
      user.username?.toLowerCase().includes(searchForm.username.toLowerCase())
    )
  }
  
  if (searchForm.phone) {
    filtered = filtered.filter(user => 
      user.phone?.includes(searchForm.phone)
    )
  }
  
  if (searchForm.profileStatus) {
    filtered = filtered.filter(user => 
      user.isProfileCompleted === searchForm.profileStatus
    )
  }
  
  if (searchForm.creditLevel) {
    filtered = filtered.filter(user => {
      const score = parseInt(user.creditScore || 700)
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

// 分页后的用户列表 - 这是修复分页问题的关键
const paginatedUserList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUserList.value.slice(start, end)
})

// 获取用户列表
const getUserList = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/users`)
    userList.value = response.data.users || []
    total.value = userList.value.length
    ElMessage.success('用户数据加载成功')
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败，请确保后端服务正在运行')
    userList.value = []
  } finally {
    loading.value = false
  }
}

// 身份证脱敏
const maskIdCard = (idCard) => {
  if (!idCard || idCard.length < 8) return idCard
  return idCard.replace(/(.{6})(.{8})(.{4})/, '$1********$3')
}

// 信用分相关工具函数
const getCreditScoreType = (score) => {
  const numScore = parseInt(score) || 700
  if (numScore >= 700) return 'success'
  if (numScore >= 650) return ''
  if (numScore >= 600) return 'warning'
  if (numScore >= 550) return 'info'
  return 'danger'
}

const getCreditScoreClass = (score) => {
  const numScore = parseInt(score) || 700
  if (numScore >= 700) return 'score-excellent'
  if (numScore >= 650) return 'score-good'
  if (numScore >= 600) return 'score-fair'
  if (numScore >= 550) return 'score-pass'
  return 'score-poor'
}

const getCreditLevel = (score) => {
  const numScore = parseInt(score) || 700
  if (numScore >= 700) return '优秀'
  if (numScore >= 650) return '良好'
  if (numScore >= 600) return '中等'
  if (numScore >= 550) return '及格'
  return '较差'
}

const getCreditDescription = (score) => {
  const numScore = parseInt(score) || 700
  if (numScore >= 700) return '信用状况优秀，可享受最优贷款条件'
  if (numScore >= 650) return '信用状况良好，可获得较好的贷款额度'
  if (numScore >= 600) return '信用状况中等，贷款审核较为严格'
  if (numScore >= 550) return '信用状况及格，建议完善个人信息提升信用分'
  return '信用状况较差，需要完善个人信息并提升信用水平'
}

// 格式化金额
const formatAmount = (amount) => {
  const num = parseFloat(amount) || 0
  return num.toLocaleString()
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  // 过滤在计算属性中处理，这里不需要重新获取数据
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  currentPage.value = 1
}

// 获取信用分计算规则
const fetchCreditRules = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/credit/rules`)
    creditRules.value = response.data.data
  } catch (error) {
    console.error('获取信用分规则失败:', error)
    ElMessage.error('获取信用分规则失败')
  }
}

// 重新计算用户信用分
const recalculateCredit = async (user) => {
  recalculatingUsers.value.push(user.username)
  try {
    // 构建用户数据
    const userData = {
      education: user.education || '',
      maritalStatus: user.maritalStatus || '',
      workStatus: user.workStatus || '',
      income: user.income || '',
      hasHouse: user.hasHouse || false,
      hasCar: user.hasCar || false,
      contactName: user.contactName || '',
      contactPhone: user.contactPhone || ''
    }
    
    const response = await axios.post(`${API_BASE_URL}/api/credit/calculate`, userData)
    const newScore = response.data.data.total_score
    
    // 更新用户信用分
    const updateResponse = await axios.put(`${API_BASE_URL}/admin/users/${user.username}/credit`, {
      creditScore: newScore
    })
    
    if (updateResponse.data.success) {
      // 更新本地数据
      const userIndex = userList.value.findIndex(u => u.username === user.username)
      if (userIndex !== -1) {
        userList.value[userIndex].creditScore = newScore.toString()
      }
      
      ElMessage.success(`用户 ${user.username} 的信用分已更新为 ${newScore} 分`)
    }
  } catch (error) {
    console.error('重新计算信用分失败:', error)
    ElMessage.error('重新计算信用分失败')
  } finally {
    recalculatingUsers.value = recalculatingUsers.value.filter(u => u !== user.username)
  }
}

// 重新计算当前用户信用分
const recalculateCurrentUserCredit = async () => {
  if (!currentUser.value) return
  
  recalculatingCurrentUser.value = true
  try {
    const userData = {
      education: currentUser.value.education || '',
      maritalStatus: currentUser.value.maritalStatus || '',
      workStatus: currentUser.value.workStatus || '',
      income: currentUser.value.income || '',
      hasHouse: currentUser.value.hasHouse || false,
      hasCar: currentUser.value.hasCar || false,
      contactName: currentUser.value.contactName || '',
      contactPhone: currentUser.value.contactPhone || ''
    }
    
    const response = await axios.post(`${API_BASE_URL}/api/credit/calculate`, userData)
    currentUserCreditDetail.value = response.data.data
    
    const newScore = response.data.data.total_score
    
    // 更新用户信用分
    const updateResponse = await axios.put(`${API_BASE_URL}/admin/users/${currentUser.value.username}/credit`, {
      creditScore: newScore
    })
    
    if (updateResponse.data.success) {
      // 更新当前用户数据
      currentUser.value.creditScore = newScore.toString()
      
      // 更新用户列表中的数据
      const userIndex = userList.value.findIndex(u => u.username === currentUser.value.username)
      if (userIndex !== -1) {
        userList.value[userIndex].creditScore = newScore.toString()
      }
      
      ElMessage.success(`信用分已更新为 ${newScore} 分`)
    }
  } catch (error) {
    console.error('重新计算信用分失败:', error)
    ElMessage.error('重新计算信用分失败')
  } finally {
    recalculatingCurrentUser.value = false
  }
}

// 查看信用分计算规则
const viewCreditRules = async () => {
  if (!creditRules.value) {
    await fetchCreditRules()
  }
  creditRulesVisible.value = true
}

// 格式化分数显示（带正负号）
const formatScoreWithSign = (score) => {
  const num = parseInt(score) || 0
  if (num > 0) return `+${num}`
  return num.toString()
}

// 格式化规则数据
const formatRuleData = (options) => {
  return Object.entries(options).map(([option, score]) => ({
    option,
    score: score >= 0 ? `+${score}分` : `${score}分`
  }))
}

// 格式化等级数据
const formatLevelData = (levels) => {
  const levelConfig = [
    { level: '优秀', tagType: 'success' },
    { level: '良好', tagType: '' },
    { level: '中等', tagType: 'warning' },
    { level: '及格', tagType: 'info' },
    { level: '较差', tagType: 'danger' }
  ]
  
  return levelConfig.map(config => ({
    level: config.level,
    range: levels[config.level],
    tagType: config.tagType
  }))
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

// 查看用户详情
const handleView = (row) => {
  currentUser.value = row
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  ElMessage.info(`编辑用户功能开发中: ${row.username}`)
  // TODO: 实现用户编辑功能
}

// 处理下拉菜单命令
const handleCommand = (command, row) => {
  switch (command) {
    case 'view':
      handleView(row)
      break
    case 'edit':
      handleEdit(row)
      break
    case 'recalculate':
      recalculateCredit(row)
      break
    case 'delete':
      handleDelete(row)
      break
    default:
      console.warn('Unknown command:', command)
  }
}

// 删除用户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${row.username} 吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    try {
      await axios.delete(`${API_BASE_URL}/admin/users/${row.username}`)
      ElMessage.success('删除成功')
      getUserList() // 重新获取用户列表
    } catch (error) {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败')
    }
  } catch {
    // 用户取消操作
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedUsers.value.length} 个用户吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    try {
      // 并发删除选中的用户
      const deletePromises = selectedUsers.value.map(user => 
        axios.delete(`${API_BASE_URL}/admin/users/${user.username}`)
      )
      
      await Promise.all(deletePromises)
      ElMessage.success('批量删除成功')
      selectedUsers.value = []
      getUserList() // 重新获取用户列表
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  } catch {
    // 用户取消操作
  }
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
  getUserList()
  fetchCreditRules()
})
</script>

<style scoped>
.user-management {
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

.table-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-stats {
  display: flex;
  gap: 12px;
}

.overdue-amount {
  color: #f56c6c;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 信用分相关样式 */
.credit-score-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.score-value {
  font-weight: bold;
  font-size: 16px;
  line-height: 1.2;
}

.score-value::after {
  content: "分";
  font-size: 12px;
  margin-left: 2px;
}

.score-excellent { color: #67C23A; }
.score-good { color: #409EFF; }
.score-fair { color: #E6A23C; }
.score-pass { color: #909399; }
.score-poor { color: #F56C6C; }

/* 信用分详情样式 */
.credit-detail {
  padding: 20px;
}

.credit-header {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  margin-bottom: 20px;
}

.current-score {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.score-number {
  font-size: 48px;
  font-weight: bold;
}

.score-unit {
  font-size: 16px;
  color: #909399;
}

.score-info {
  flex: 1;
}

.score-level {
  margin-bottom: 8px;
}

.score-desc {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.score-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.credit-breakdown {
  margin-top: 20px;
}

.no-credit-detail {
  padding: 40px;
  text-align: center;
}

/* 信息完整度样式 */
.info-completeness {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.completeness-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 4px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.completeness-item.complete {
  background: #f0f9ff;
  border-left: 4px solid #67C23A;
}

.completeness-item .el-icon {
  font-size: 18px;
  color: #909399;
}

.completeness-item.complete .el-icon {
  color: #67C23A;
}

.completeness-item span {
  flex: 1;
  font-weight: 500;
}

/* 信用分计算规则样式 */
.credit-rules-content {
  padding: 20px;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 桌面端布局 */
.desktop-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mobile-actions {
  display: none;
}

/* 按钮组样式优化 */
.el-button-group .el-button {
  border-radius: 0;
}

.el-button-group .el-button:first-child {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.el-button-group .el-button:last-child {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

/* 悬停效果 */
.desktop-actions .el-button {
  transition: all 0.3s ease;
}

.desktop-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .desktop-actions .el-button-group .el-button span {
    display: none;
  }
  
  .desktop-actions .el-button-group .el-button {
    min-width: 32px;
    padding: 8px 10px;
  }
}

@media (max-width: 992px) {
  .desktop-actions {
    display: none;
  }
  
  .mobile-actions {
    display: flex;
  }
}

/* 下拉菜单样式优化 */
.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
}

.el-dropdown-menu__item .el-icon {
  font-size: 16px;
}

/* 危险操作样式 */
.danger-item {
  color: #f56c6c !important;
}

.danger-item:hover {
  background-color: #fef0f0 !important;
  color: #f56c6c !important;
}

.danger-item .el-icon {
  color: #f56c6c !important;
}

/* 更多按钮样式 */
.desktop-actions .el-dropdown .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.desktop-actions .el-dropdown .el-button .el-icon--right {
  margin-left: 0;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.desktop-actions .el-dropdown.is-opened .el-button .el-icon--right {
  transform: rotate(180deg);
}
</style> 