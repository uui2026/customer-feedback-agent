<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">反馈总量</span>
              <span class="stat-value">{{ stats.totalFeedback }}</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#409eff">
              <ChatDotRound />
            </el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">今日新增</span>
              <span class="stat-value">{{ stats.todayCount }}</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#67c23a">
              <TrendCharts />
            </el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">待处理工单</span>
              <span class="stat-value">{{ stats.pendingTickets }}</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#e6a23c">
              <Tickets />
            </el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">SLA达标率</span>
              <span class="stat-value">{{ stats.slaRate }}%</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#909399">
              <CircleCheck />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">渠道分布</span>
          </template>
          <v-chart :option="channelChartOption" autoresize style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">意图分布</span>
          </template>
          <v-chart :option="intentChartOption" autoresize style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">7日趋势</span>
          </template>
          <v-chart :option="trendChartOption" autoresize style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">情感分布</span>
          </template>
          <v-chart :option="sentimentChartOption" autoresize style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部区域 -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">最近反馈</span>
          </template>
          <el-table :data="recentFeedback" stripe size="small" max-height="320">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="channel" label="渠道" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.channel }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
            <el-table-column prop="sentiment" label="情感" width="90">
              <template #default="{ row }">
                <el-tag
                  :type="sentimentType(row.sentiment)"
                  size="small"
                >{{ row.sentiment }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">SLA预警</span>
            <el-badge :value="slaAlerts.length" :max="99" class="alert-badge" />
          </template>
          <div class="sla-alerts">
            <div v-for="alert in slaAlerts" :key="alert.id" class="sla-alert-item">
              <el-alert
                :title="`工单 #${alert.ticket_id} 即将超时`"
                :description="`剩余 ${alert.remaining_hours} 小时 - ${alert.team}`"
                type="warning"
                show-icon
                :closable="false"
              />
            </div>
            <el-empty v-if="slaAlerts.length === 0" description="暂无预警" :image-size="80" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import {
  ChatDotRound,
  TrendCharts,
  Tickets,
  CircleCheck
} from '@element-plus/icons-vue'
import {
  getDashboardStats,
  getChannelDistribution,
  getIntentDistribution,
  getSentimentDistribution,
  getTrendData,
  getRecentFeedback,
  getSlaAlerts
} from '@/api/dashboard'

const stats = ref({
  totalFeedback: 0,
  todayCount: 0,
  pendingTickets: 0,
  slaRate: 0
})

const recentFeedback = ref([])
const slaAlerts = ref([])

const channelChartOption = ref({})
const intentChartOption = ref({})
const trendChartOption = ref({})
const sentimentChartOption = ref({})

const formatTime = (t) => t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '-'

const sentimentType = (s) => {
  const map = { '正面': 'success', '负面': 'danger', '中性': 'info' }
  return map[s] || 'info'
}

const loadDashboard = async () => {
  try {
    const [statsRes, channelRes, intentRes, sentimentRes, trendRes, recentRes, slaRes] = await Promise.allSettled([
      getDashboardStats(),
      getChannelDistribution(),
      getIntentDistribution(),
      getSentimentDistribution(),
      getTrendData(7),
      getRecentFeedback(10),
      getSlaAlerts()
    ])

    if (statsRes.status === 'fulfilled') {
      stats.value = statsRes.value
    }

    if (channelRes.status === 'fulfilled') {
      const data = channelRes.value || []
      channelChartOption.value = {
        tooltip: { trigger: 'item' },
        legend: { bottom: 0 },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6 },
          label: { show: true, formatter: '{b}: {c} ({d}%)' },
          data: data.map(d => ({ name: d.name, value: d.value }))
        }]
      }
    }

    if (intentRes.status === 'fulfilled') {
      const data = intentRes.value || []
      intentChartOption.value = {
        tooltip: { trigger: 'axis' },
        grid: { left: 80, right: 20, top: 20, bottom: 40 },
        xAxis: {
          type: 'category',
          data: data.map(d => d.name),
          axisLabel: { rotate: 30 }
        },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar',
          data: data.map(d => d.value),
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#409eff' }, { offset: 1, color: '#79bbff' }] }
          }
        }]
      }
    }

    if (sentimentRes.status === 'fulfilled') {
      const data = sentimentRes.value || []
      const colorMap = { '正面': '#67c23a', '负面': '#f56c6c', '中性': '#909399' }
      sentimentChartOption.value = {
        tooltip: { trigger: 'item' },
        legend: { bottom: 0 },
        series: [{
          type: 'pie',
          radius: '65%',
          data: data.map(d => ({
            name: d.name,
            value: d.value,
            itemStyle: { color: colorMap[d.name] || '#409eff' }
          }))
        }]
      }
    }

    if (trendRes.status === 'fulfilled') {
      const data = trendRes.value || []
      trendChartOption.value = {
        tooltip: { trigger: 'axis' },
        grid: { left: 50, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: 'category',
          data: data.map(d => d.date),
          axisLabel: { formatter: (v) => dayjs(v).format('MM-DD') }
        },
        yAxis: { type: 'value' },
        series: [{
          type: 'line',
          data: data.map(d => d.count),
          smooth: true,
          areaStyle: {
            color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#409eff33' }, { offset: 1, color: '#409eff05' }] }
          },
          lineStyle: { color: '#409eff', width: 2 },
          itemStyle: { color: '#409eff' }
        }]
      }
    }

    if (recentRes.status === 'fulfilled') {
      recentFeedback.value = recentRes.value || []
    }

    if (slaRes.status === 'fulfilled') {
      slaAlerts.value = slaRes.value || []
    }
  } catch (e) {
    console.error('加载仪表盘数据失败', e)
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-icon {
  opacity: 0.8;
}

.chart-card {
  border-radius: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.alert-badge {
  margin-left: 8px;
}

.sla-alerts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 280px;
  overflow-y: auto;
}

.sla-alert-item {
  width: 100%;
}
</style>
