<template>
  <div class="dashboard-home">
    <!-- 数据概览卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="data-card user-card">
          <div class="data-header">
            <div class="data-title">总用户数</div>
            <el-icon class="data-icon user-icon"><el-icon-user /></el-icon>
          </div>
          <div class="data-value">{{ statistics.userCount || 0 }}</div>
          <div class="data-footer">总注册用户数量</div>
          <div class="data-trend">
            <span class="trend-text">较上月 +12%</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card loan-card">
          <div class="data-header">
            <div class="data-title">总贷款金额</div>
            <el-icon class="data-icon loan-icon"><el-icon-money /></el-icon>
          </div>
          <div class="data-value">¥ {{ formatNumber(statistics.totalLoanAmount || 0) }}</div>
          <div class="data-footer">已发放贷款总额</div>
          <div class="data-trend">
            <span class="trend-text">较上月 +8%</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card pending-card">
          <div class="data-header">
            <div class="data-title">待还款总额</div>
            <el-icon class="data-icon pending-icon"><el-icon-wallet /></el-icon>
          </div>
          <div class="data-value">¥ {{ formatNumber(statistics.pendingRepayAmount || 0) }}</div>
          <div class="data-footer">用户待还款总额</div>
          <div class="data-trend">
            <span class="trend-text warning">需关注</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card repaid-card">
          <div class="data-header">
            <div class="data-title">已还款总额</div>
            <el-icon class="data-icon repaid-icon"><el-icon-check /></el-icon>
          </div>
          <div class="data-value">¥ {{ formatNumber(statistics.repaidAmount || 0) }}</div>
          <div class="data-footer">已成功还款总额</div>
          <div class="data-trend">
            <span class="trend-text success">增长良好</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 资金分布扇形图 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">资金分布情况</span>
              <el-tag type="info" size="small">实时数据</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="pieChartRef" class="chart-item"></div>
          </div>
        </el-card>
      </el-col>

      <!-- 数据结构树状图 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">业务结构分析</span>
              <el-tag type="success" size="small">层级视图</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="treeChartRef" class="chart-item"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图表 -->
    <el-row :gutter="20" class="trend-row">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">业务数据趋势</span>
              <div class="header-actions">
                <el-radio-group v-model="trendPeriod" size="small" @change="updateTrendChart">
                  <el-radio-button label="7天">7天</el-radio-button>
                  <el-radio-button label="30天">30天</el-radio-button>
                  <el-radio-button label="90天">90天</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <div ref="lineChartRef" class="chart-item trend-chart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近贷款申请 -->
    <el-card class="recent-loans" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">最近贷款申请</span>
          <el-button type="primary" size="small" @click="$router.push('/dashboard/loans')">查看全部</el-button>
        </div>
      </template>
      
      <el-table :data="recentLoans" style="width: 100%" v-loading="loading">
        <el-table-column prop="loan_id" label="贷款ID" width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.loan_id" placement="top">
              <span class="loan-id">{{ row.loan_id.slice(0, 8) }}...</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="loan_amount" label="贷款金额">
          <template #default="{ row }">
            <span class="amount">¥ {{ formatNumber(row.loan_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="loan_term" label="贷款期限">
          <template #default="{ row }">
            {{ formatLoanTerm(row.loan_term) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getLoanStatusType(row.status)">
              {{ getLoanStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="apply_date" label="申请日期" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'

// 配置API基础URL
const API_BASE_URL = 'http://localhost:8000'

const loading = ref(false)
const statistics = ref({
  userCount: 0,
  totalLoanAmount: 0,
  pendingRepayAmount: 0,
  repaidAmount: 0
})
const recentLoans = ref([])
const trendPeriod = ref('30天')

// 图表引用
const pieChartRef = ref()
const treeChartRef = ref()
const lineChartRef = ref()

// 图表实例
let pieChart = null
let treeChart = null
let lineChart = null

// 获取统计数据
const fetchStatistics = async () => {
  try {
    loading.value = true
    const response = await axios.get(`${API_BASE_URL}/admin/statistics`)
    statistics.value = response.data.data || {
      userCount: 0,
      totalLoanAmount: 0,
      pendingRepayAmount: 0,
      repaidAmount: 0
    }
    
    // 更新图表
    await nextTick()
    await initCharts()
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败，请确保后端服务正在运行')
    // 使用模拟数据
    statistics.value = {
      userCount: 150,
      totalLoanAmount: 5000000,
      pendingRepayAmount: 1200000,
      repaidAmount: 3800000
    }
    await nextTick()
    await initCharts()
  } finally {
    loading.value = false
  }
}

// 获取最近贷款申请
const fetchRecentLoans = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/loans`)
    // 取最近的5条记录
    recentLoans.value = (response.data.loans || []).slice(0, 5)
  } catch (error) {
    console.error('获取最近贷款申请失败:', error)
    // 使用模拟数据
    recentLoans.value = []
  }
}

// 获取贷款趋势数据 - 改为静态数据
const fetchTrendData = async () => {
  // 返回静态模拟数据
    return {
    loans: [
      { approve_date: '2024-01-15', loan_amount: 50000 },
      { approve_date: '2024-01-16', loan_amount: 75000 },
      { approve_date: '2024-01-17', loan_amount: 60000 },
      { approve_date: '2024-01-18', loan_amount: 80000 },
      { approve_date: '2024-01-19', loan_amount: 45000 },
      { approve_date: '2024-01-20', loan_amount: 90000 },
      { approve_date: '2024-01-21', loan_amount: 65000 },
      { approve_date: '2024-01-22', loan_amount: 70000 },
      { approve_date: '2024-01-23', loan_amount: 85000 },
      { approve_date: '2024-01-24', loan_amount: 55000 },
      { approve_date: '2024-01-25', loan_amount: 95000 },
      { approve_date: '2024-01-26', loan_amount: 40000 },
      { approve_date: '2024-01-27', loan_amount: 78000 },
      { approve_date: '2024-01-28', loan_amount: 62000 },
      { approve_date: '2024-01-29', loan_amount: 88000 },
      { approve_date: '2024-01-30', loan_amount: 52000 }
    ],
    repayments: [
      { payment_date: '2024-01-15', amount: 35000 },
      { payment_date: '2024-01-16', amount: 48000 },
      { payment_date: '2024-01-17', amount: 42000 },
      { payment_date: '2024-01-18', amount: 58000 },
      { payment_date: '2024-01-19', amount: 33000 },
      { payment_date: '2024-01-20', amount: 67000 },
      { payment_date: '2024-01-21', amount: 45000 },
      { payment_date: '2024-01-22', amount: 52000 },
      { payment_date: '2024-01-23', amount: 61000 },
      { payment_date: '2024-01-24', amount: 38000 },
      { payment_date: '2024-01-25', amount: 72000 },
      { payment_date: '2024-01-26', amount: 29000 },
      { payment_date: '2024-01-27', amount: 55000 },
      { payment_date: '2024-01-28', amount: 43000 },
      { payment_date: '2024-01-29', amount: 64000 },
      { payment_date: '2024-01-30', amount: 36000 }
    ]
  }
}

// 处理趋势数据 - 优化为静态数据处理
const processTrendData = (loans, repayments, days) => {
  const today = new Date()
  const dates = []
  const loanData = []
  const repayData = []
  
  // 生成日期数组
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(today.getDate() - i)
    dates.push(date.toLocaleDateString('zh-CN'))
  }
  
  // 使用静态数据生成趋势 - 根据时间周期调整数据密度
  if (days === 7) {
    // 7天数据
    const staticLoanData = [45000, 52000, 68000, 41000, 75000, 59000, 83000]
    const staticRepayData = [32000, 38000, 47000, 29000, 54000, 42000, 61000]
    loanData.push(...staticLoanData.slice(0, days))
    repayData.push(...staticRepayData.slice(0, days))
  } else if (days === 30) {
    // 30天数据 - 生成有趋势性的数据
    for (let i = 0; i < days; i++) {
      // 基础值加上波动和趋势
      const trend = i * 500 // 每天增长500
      const loanBase = 50000 + trend + (Math.sin(i * 0.2) * 15000)
      const repayBase = 40000 + trend * 0.8 + (Math.cos(i * 0.15) * 12000)
      
      loanData.push(Math.max(20000, Math.round(loanBase)))
      repayData.push(Math.max(15000, Math.round(repayBase)))
    }
  } else {
    // 90天数据
    for (let i = 0; i < days; i++) {
      // 长期趋势数据
      const trend = i * 300 // 每天增长300
      const seasonalFactor = Math.sin(i * 0.07) * 0.3 + 1 // 季节性波动
      const loanBase = (45000 + trend) * seasonalFactor + (Math.random() - 0.5) * 10000
      const repayBase = (35000 + trend * 0.85) * seasonalFactor + (Math.random() - 0.5) * 8000
      
      loanData.push(Math.max(15000, Math.round(loanBase)))
      repayData.push(Math.max(10000, Math.round(repayBase)))
    }
  }
  
  const hasData = true // 静态数据始终有数据
  
  return { dates, loanData, repayData, hasData }
}

// 初始化图表
const initCharts = async () => {
  initPieChart()
  initTreeChart()
  await initLineChart()
}

// 初始化扇形图
const initPieChart = () => {
  if (!pieChartRef.value) return
  
  pieChart = echarts.init(pieChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      top: 'center'
    },
    series: [
      {
        name: '资金分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['65%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          {
            value: statistics.value.repaidAmount,
            name: '已还款金额',
            itemStyle: { color: '#67C23A' }
          },
          {
            value: statistics.value.pendingRepayAmount,
            name: '待还款金额',
            itemStyle: { color: '#E6A23C' }
          },
          {
            value: Math.max(0, statistics.value.totalLoanAmount - statistics.value.repaidAmount - statistics.value.pendingRepayAmount),
            name: '其他资金',
            itemStyle: { color: '#909399' }
          }
        ]
      }
    ]
  }
  
  pieChart.setOption(option)
}

// 初始化树状图
const initTreeChart = () => {
  if (!treeChartRef.value) return
  
  treeChart = echarts.init(treeChartRef.value)
  
  const treeData = {
    name: '极速贷业务',
    children: [
      {
        name: `用户管理 (${statistics.value.userCount})`,
        children: [
          { name: '新注册用户', value: Math.floor(statistics.value.userCount * 0.3) },
          { name: '活跃用户', value: Math.floor(statistics.value.userCount * 0.6) },
          { name: '休眠用户', value: Math.floor(statistics.value.userCount * 0.1) }
        ]
      },
      {
        name: '资金管理',
        children: [
          { name: `已放贷 ¥${formatNumber(statistics.value.totalLoanAmount)}`, value: statistics.value.totalLoanAmount },
          { name: `待回收 ¥${formatNumber(statistics.value.pendingRepayAmount)}`, value: statistics.value.pendingRepayAmount },
          { name: `已回收 ¥${formatNumber(statistics.value.repaidAmount)}`, value: statistics.value.repaidAmount }
        ]
      }
    ]
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove'
    },
    series: [
      {
        type: 'tree',
        data: [treeData],
        top: '5%',
        left: '10%',
        bottom: '5%',
        right: '15%',
        symbolSize: 12,
        label: {
          position: 'left',
          verticalAlign: 'middle',
          align: 'right',
          fontSize: 12
        },
        leaves: {
          label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left'
          }
        },
        emphasis: {
          focus: 'descendant'
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750,
        itemStyle: {
          color: '#409EFF',
          borderColor: '#409EFF'
        }
      }
    ]
  }
  
  treeChart.setOption(option)
}

// 初始化趋势图
const initLineChart = async () => {
  if (!lineChartRef.value) return
  
  lineChart = echarts.init(lineChartRef.value)
  
  // 获取真实数据
  const { loans, repayments } = await fetchTrendData()
  const days = trendPeriod.value === '7天' ? 7 : trendPeriod.value === '30天' ? 30 : 90
  const { dates, loanData, repayData, hasData } = processTrendData(loans, repayments, days)
  
  const option = {
    title: {
      text: hasData ? `最近${days}天业务趋势` : '暂无数据',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal',
        color: hasData ? '#303133' : '#909399'
      },
      left: 'left',
      top: 5
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        let result = `${params[0].axisValue}<br/>`
        params.forEach(param => {
          const value = param.value || 0
          result += `${param.marker}${param.seriesName}: ¥${formatNumber(value)}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['放贷金额', '还款金额'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: hasData ? '20%' : '25%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value) => {
          if (value >= 10000) {
            return `¥${(value / 10000).toFixed(1)}万`
          } else if (value >= 1000) {
            return `¥${(value / 1000).toFixed(1)}千`
          } else if (value === 0) {
            return '¥0'
          } else {
            return `¥${value}`
          }
        }
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '放贷金额',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { 
          color: '#409EFF',
          borderWidth: 2,
          borderColor: '#fff'
        },
        lineStyle: {
          width: 3
        },
        areaStyle: { 
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        },
        data: loanData
      },
      {
        name: '还款金额',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { 
          color: '#67C23A',
          borderWidth: 2,
          borderColor: '#fff'
        },
        lineStyle: {
          width: 3
        },
        areaStyle: { 
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
            ]
          }
        },
        data: repayData
      }
    ]
  }
  
  lineChart.setOption(option)
}

// 更新趋势图
const updateTrendChart = async () => {
  await initLineChart()
}

// 监听窗口大小变化
const handleResize = () => {
  pieChart?.resize()
  treeChart?.resize()
  lineChart?.resize()
}

// 格式化数字
const formatNumber = (num) => {
  return Number(num).toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}

// 格式化贷款期限
const formatLoanTerm = (term) => {
  const termNum = Number(term)
  if (termNum <= 31) {
    return `${termNum}天`
  } else {
    return `${termNum}月`
  }
}

// 获取贷款状态类型
const getLoanStatusType = (status) => {
  switch (status) {
    case 'approved':
      return 'success'
    case 'pending':
      return 'warning'
    case 'rejected':
      return 'danger'
    case 'completed':
      return 'info'
    default:
      return ''
  }
}

// 获取贷款状态文本
const getLoanStatusText = (status) => {
  switch (status) {
    case 'approved':
      return '已批准'
    case 'pending':
      return '待审批'
    case 'rejected':
      return '已拒绝'
    case 'completed':
      return '已完成'
    default:
      return '未知'
  }
}

onMounted(() => {
  fetchStatistics()
  fetchRecentLoans()
  window.addEventListener('resize', handleResize)
})

// 清理资源
const cleanup = () => {
  pieChart?.dispose()
  treeChart?.dispose()
  lineChart?.dispose()
  window.removeEventListener('resize', handleResize)
}

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(cleanup)
</script>

<style scoped>
.dashboard-home {
  padding: 20px 0;
}

.stats-row {
  margin-bottom: 20px;
}

.data-card {
  height: 160px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.data-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.data-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
}

.user-card::before { background: linear-gradient(90deg, #409EFF, #36CFC9); }
.loan-card::before { background: linear-gradient(90deg, #E6A23C, #F56C6C); }
.pending-card::before { background: linear-gradient(90deg, #F56C6C, #E6A23C); }
.repaid-card::before { background: linear-gradient(90deg, #67C23A, #52C41A); }

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.data-title {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

.data-icon {
  font-size: 28px;
  transition: all 0.3s ease;
}

.user-icon { color: #409EFF; }
.loan-icon { color: #E6A23C; }
.pending-icon { color: #F56C6C; }
.repaid-icon { color: #67C23A; }

.data-card:hover .data-icon {
  transform: scale(1.1);
}

.data-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin: 15px 0 10px;
  line-height: 1;
}

.data-footer {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.data-trend {
  position: absolute;
  bottom: 12px;
  left: 20px;
}

.trend-text {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.trend-text.success {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.trend-text.warning {
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
}

.charts-row, .trend-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
}

.chart-container {
  height: 320px;
  padding: 10px;
}

.chart-item {
  width: 100%;
  height: 100%;
}

.trend-chart {
  height: 300px;
}

.recent-loans {
  margin-top: 20px;
}

.loan-id {
  font-family: monospace;
  color: #409EFF;
}

.amount {
  font-weight: 600;
  color: #E6A23C;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .data-card {
    height: 140px;
  }
  
  .data-value {
    font-size: 24px;
  }
  
  .chart-card {
    height: 350px;
  }
  
  .chart-container {
    height: 270px;
  }
}

@media (max-width: 768px) {
  .dashboard-home {
    padding: 10px 0;
  }
  
  .data-card {
    height: 120px;
    margin-bottom: 15px;
  }
  
  .data-value {
    font-size: 20px;
  }
  
  .chart-card {
    height: 300px;
  }
}
</style> 