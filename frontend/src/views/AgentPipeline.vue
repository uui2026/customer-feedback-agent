<template>
  <div class="agent-pipeline">
    <!-- 全管线操作 -->
    <el-card shadow="hover" class="pipeline-header">
      <div class="header-content">
        <div class="header-info">
          <h3>智能体管线</h3>
          <p>管理与监控5个智能体的数据处理流水线</p>
        </div>
        <div class="header-actions">
          <el-button
            :type="pipelineRunning ? 'danger' : 'primary'"
            size="large"
            @click="triggerFullPipeline"
          >
            <el-icon v-if="!pipelineRunning"><VideoPlay /></el-icon>
            <el-icon v-else><VideoPause /></el-icon>
            {{ pipelineRunning ? '停止管线' : '启动全管线' }}
          </el-button>
          <el-button size="large" @click="refreshStatus" :loading="statusLoading">
            <el-icon><Refresh /></el-icon>
            刷新状态
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 管线可视化 -->
    <el-card shadow="hover" class="pipeline-visual">
      <template #header>
        <span class="card-title">管线流程图</span>
      </template>
      <div class="pipeline-flow">
        <div
          v-for="(agent, index) in agents"
          :key="agent.name"
          class="pipeline-node-wrapper"
        >
          <div
            class="pipeline-node"
            :class="{ active: agent.status === 'running', success: agent.status === 'completed', error: agent.status === 'error' }"
            @click="selectAgent(agent)"
          >
            <div class="node-icon">
              <el-icon :size="28">
                <component :is="agent.icon" />
              </el-icon>
            </div>
            <div class="node-label">{{ agent.label }}</div>
            <div class="node-status">
              <el-tag :type="statusTagType(agent.status)" size="small" effect="dark">
                {{ statusLabel(agent.status) }}
              </el-tag>
            </div>
            <el-button
              class="node-trigger"
              type="primary"
              size="small"
              :loading="agent.triggering"
              @click.stop="triggerSingleAgent(agent)"
            >
              触发
            </el-button>
          </div>
          <div v-if="index < agents.length - 1" class="pipeline-arrow">
            <el-icon :size="24"><Right /></el-icon>
          </div>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="pipeline-bottom">
      <!-- 各智能体状态 -->
      <el-col :span="10">
        <el-card shadow="hover" class="agent-status-card">
          <template #header>
            <span class="card-title">智能体状态</span>
          </template>
          <div class="agent-status-list">
            <div
              v-for="agent in agents"
              :key="agent.name"
              class="agent-status-item"
              :class="{ 'is-active': selectedAgent?.name === agent.name }"
              @click="selectAgent(agent)"
            >
              <div class="agent-status-left">
                <el-icon :size="18" :color="agentColor(agent.status)">
                  <component :is="agent.icon" />
                </el-icon>
                <div>
                  <div class="agent-name">{{ agent.label }}</div>
                  <div class="agent-desc">{{ agent.description }}</div>
                </div>
              </div>
              <div class="agent-status-right">
                <el-tag :type="statusTagType(agent.status)" size="small">
                  {{ statusLabel(agent.status) }}
                </el-tag>
                <div v-if="agent.lastRun" class="agent-last-run">
                  上次运行: {{ formatTime(agent.lastRun) }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 处理日志 -->
      <el-col :span="14">
        <el-card shadow="hover" class="log-card">
          <template #header>
            <div class="log-header">
              <span class="card-title">处理日志</span>
              <div>
                <el-select v-model="logFilter" size="small" style="width: 130px" @change="loadLogs">
                  <el-option label="全部日志" value="all" />
                  <el-option
                    v-for="agent in agents"
                    :key="agent.name"
                    :label="agent.label"
                    :value="agent.name"
                  />
                </el-select>
                <el-button size="small" @click="loadLogs" style="margin-left: 8px">刷新</el-button>
              </div>
            </div>
          </template>
          <div class="log-container" ref="logContainer">
            <div v-if="logs.length === 0" class="empty-log">
              <el-empty description="暂无日志" :image-size="60" />
            </div>
            <div v-for="log in logs" :key="log.id" class="log-item">
              <div class="log-meta">
                <el-tag :type="logLevelType(log.level)" size="small">{{ log.level }}</el-tag>
                <span class="log-agent">{{ agentLabel(log.agent) }}</span>
                <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              </div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  Refresh,
  Right,
  Download,
  Aim,
  Switch,
  ChatLineRound,
  DataAnalysis
} from '@element-plus/icons-vue'
import {
  getPipelineStatus,
  triggerFullPipeline as apiTriggerFullPipeline,
  triggerAgent,
  getAllAgentsStatus,
  getAgentLogs
} from '@/api/agent'

const pipelineRunning = ref(false)
const statusLoading = ref(false)
const selectedAgent = ref(null)
const logFilter = ref('all')
const logs = ref([])
const logContainer = ref(null)

const agents = reactive([
  {
    name: 'data-collector',
    label: '数据采集',
    description: '多渠道反馈数据采集与清洗',
    icon: 'Download',
    status: 'idle',
    triggering: false,
    lastRun: null
  },
  {
    name: 'intent-analyzer',
    label: '意图分析',
    description: '反馈意图识别与情感分析',
    icon: 'Aim',
    status: 'idle',
    triggering: false,
    lastRun: null
  },
  {
    name: 'ticket-router',
    label: '工单路由',
    description: '自动创建工单并分配团队',
    icon: 'Switch',
    status: 'idle',
    triggering: false,
    lastRun: null
  },
  {
    name: 'reply-generator',
    label: '回复生成',
    description: '基于知识库生成智能回复',
    icon: 'ChatLineRound',
    status: 'idle',
    triggering: false,
    lastRun: null
  },
  {
    name: 'review-analyzer',
    label: '回顾分析',
    description: '数据回顾与趋势分析报告',
    icon: 'DataAnalysis',
    status: 'idle',
    triggering: false,
    lastRun: null
  }
])

const statusTagType = (status) => {
  const map = { idle: 'info', running: 'warning', completed: 'success', error: 'danger' }
  return map[status] || 'info'
}

const statusLabel = (status) => {
  const map = { idle: '空闲', running: '运行中', completed: '已完成', error: '错误' }
  return map[status] || status
}

const agentColor = (status) => {
  const map = { idle: '#909399', running: '#e6a23c', completed: '#67c23a', error: '#f56c6c' }
  return map[status] || '#909399'
}

const agentLabel = (name) => {
  const agent = agents.find(a => a.name === name)
  return agent?.label || name
}

const logLevelType = (level) => {
  const map = { info: '', warning: 'warning', error: 'danger', success: 'success' }
  return map[level] || 'info'
}

const formatTime = (t) => t ? dayjs(t).format('YYYY-MM-DD HH:mm:ss') : '-'

const selectAgent = (agent) => {
  selectedAgent.value = agent
}

const refreshStatus = async () => {
  statusLoading.value = true
  try {
    const res = await getAllAgentsStatus()
    if (Array.isArray(res)) {
      res.forEach(item => {
        const agent = agents.find(a => a.name === item.name)
        if (agent) {
          agent.status = item.status || 'idle'
          agent.lastRun = item.last_run || null
        }
      })
    }
    const pipeline = await getPipelineStatus()
    pipelineRunning.value = pipeline?.running || false
  } catch (e) {
    console.error('刷新状态失败', e)
  } finally {
    statusLoading.value = false
  }
}

const triggerFullPipelineFn = async () => {
  if (pipelineRunning.value) {
    // 如果正在运行，点击则停止
    pipelineRunning.value = false
    agents.forEach(a => { a.status = 'idle'; a.triggering = false })
    ElMessage.info('管线已停止')
    return
  }
  try {
    pipelineRunning.value = true
    // 逐个agent显示运行状态，模拟管线逐步执行
    for (let i = 0; i < agents.length; i++) {
      if (!pipelineRunning.value) break // 被停止了
      agents[i].status = 'running'
      await new Promise(r => setTimeout(r, 400)) // 每个agent间隔400ms
    }
    // 调用后端API
    await apiTriggerFullPipeline({})
    if (pipelineRunning.value) {
      agents.forEach(a => { a.status = 'completed' })
      ElMessage.success('全管线已完成处理')
      refreshStatus()
      loadLogs()
    }
  } catch (e) {
    agents.forEach(a => { a.status = 'error' })
    ElMessage.error('启动管线失败: ' + (e.message || '未知错误'))
    console.error('启动管线失败', e)
  } finally {
    pipelineRunning.value = false
  }
}

const triggerFullPipeline = triggerFullPipelineFn

const triggerSingleAgent = async (agent) => {
  agent.triggering = true
  agent.status = 'running'
  try {
    await triggerAgent(agent.name, {})
    agent.status = 'completed'
    agent.lastRun = new Date().toISOString()
    ElMessage.success(`${agent.label} 执行完成`)
    loadLogs()
  } catch (e) {
    agent.status = 'error'
    console.error(`${agent.label} 执行失败`, e)
  } finally {
    agent.triggering = false
  }
}

const loadLogs = async () => {
  try {
    const params = {}
    if (logFilter.value !== 'all') {
      params.agent = logFilter.value
    }
    const res = await getAgentLogs(params)
    logs.value = (res?.items || res || []).reverse()
  } catch (e) {
    console.error('加载日志失败', e)
  }
}

let pollTimer = null

const pollStatus = () => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const pipeline = await getPipelineStatus()
      if (!pipeline?.running) {
        pipelineRunning.value = false
        clearInterval(pollTimer)
        pollTimer = null
        refreshStatus()
        loadLogs()
      }
    } catch {
      clearInterval(pollTimer)
      pipelineRunning.value = false
    }
  }, 3000)
}

onMounted(() => {
  refreshStatus()
  loadLogs()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.agent-pipeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pipeline-header .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h3 {
  margin: 0 0 4px;
  font-size: 18px;
  color: #303133;
}

.header-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.pipeline-visual {
  border-radius: 8px;
}

.pipeline-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 30px 20px;
  overflow-x: auto;
}

.pipeline-node-wrapper {
  display: flex;
  align-items: center;
  gap: 0;
}

.pipeline-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border-radius: 12px;
  border: 2px solid #e4e7ed;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 120px;
}

.pipeline-node:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.pipeline-node.active {
  border-color: #e6a23c;
  background: #fdf6ec;
  animation: pulse 2s infinite;
}

.pipeline-node.success {
  border-color: #67c23a;
  background: #f0f9eb;
}

.pipeline-node.error {
  border-color: #f56c6c;
  background: #fef0f0;
}

.node-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}

.pipeline-node.active .node-icon {
  background: #faecd8;
  color: #e6a23c;
}

.pipeline-node.success .node-icon {
  background: #f0f9eb;
  color: #67c23a;
}

.pipeline-node.error .node-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.node-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.node-trigger {
  margin-top: 4px;
}

.pipeline-arrow {
  display: flex;
  align-items: center;
  color: #c0c4cc;
  padding: 0 4px;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(230, 162, 60, 0.4); }
  50% { box-shadow: 0 0 0 10px rgba(230, 162, 60, 0); }
}

.pipeline-bottom {
  margin-top: 0;
}

.agent-status-card, .log-card {
  border-radius: 8px;
}

.agent-status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.agent-status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-status-item:hover, .agent-status-item.is-active {
  background: #f5f7fa;
  border-color: #409eff;
}

.agent-status-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.agent-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.agent-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.agent-status-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.agent-last-run {
  font-size: 11px;
  color: #c0c4cc;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-container {
  height: 500px;
  overflow-y: auto;
  background: #1e1e1e;
  border-radius: 8px;
  padding: 12px;
}

.empty-log {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.log-item {
  padding: 8px 0;
  border-bottom: 1px solid #333;
}

.log-item:last-child {
  border-bottom: none;
}

.log-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.log-agent {
  font-size: 12px;
  color: #79bbff;
}

.log-time {
  font-size: 11px;
  color: #666;
}

.log-message {
  font-size: 13px;
  color: #ddd;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  line-height: 1.5;
  word-break: break-all;
}
</style>
