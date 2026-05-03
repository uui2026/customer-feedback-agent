<template>
  <div class="feedback-list">
    <!-- 筛选栏 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :model="filters" inline class="filter-form">
        <el-form-item label="渠道">
          <el-select v-model="filters.channel" placeholder="全部渠道" clearable style="width: 140px">
            <el-option label="企业微信" value="wecom" />
            <el-option label="抖音" value="douyin" />
            <el-option label="邮件" value="email" />
          </el-select>
        </el-form-item>
        <el-form-item label="意图">
          <el-select v-model="filters.intent" placeholder="全部意图" clearable style="width: 140px">
            <el-option label="咨询" value="inquiry" />
            <el-option label="投诉" value="complaint" />
            <el-option label="建议" value="suggestion" />
            <el-option label="表扬" value="praise" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已回复" value="replied" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item label="搜索">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索反馈内容"
            clearable
            style="width: 200px"
            @keyup.enter="loadData"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="batchCollect" :loading="collecting">
        <el-icon><Download /></el-icon>
        批量采集
      </el-button>
      <el-button @click="loadData" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table
        :data="feedbackList"
        v-loading="loading"
        stripe
        highlight-current-row
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="channel" label="渠道" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ channelMap[row.channel] || row.channel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容预览" show-overflow-tooltip min-width="200">
          <template #default="{ row }">
            {{ row.content?.slice(0, 80) }}{{ row.content?.length > 80 ? '...' : '' }}
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="intent" label="意图" width="100">
          <template #default="{ row }">
            <el-tag :type="intentTagType(row.intent)" size="small">
              {{ intentMap[row.intent] || row.intent }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sentiment" label="情感" width="90">
          <template #default="{ row }">
            <el-tag :type="sentimentTagType(row.sentiment)" size="small">
              {{ row.sentiment }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-area">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="`反馈详情 #${currentFeedback?.id}`"
      size="500px"
      direction="rtl"
    >
      <div class="detail-content" v-if="currentFeedback">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="渠道">
            <el-tag>{{ channelMap[currentFeedback.channel] || currentFeedback.channel }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户名称">{{ currentFeedback.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="意图">
            <el-tag :type="intentTagType(currentFeedback.intent)">
              {{ intentMap[currentFeedback.intent] || currentFeedback.intent }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="情感">
            <el-tag :type="sentimentTagType(currentFeedback.sentiment)">
              {{ currentFeedback.sentiment }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTagType(currentFeedback.status)">
              {{ statusMap[currentFeedback.status] || currentFeedback.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(currentFeedback.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>反馈内容</h4>
          <div class="content-box">{{ currentFeedback.content }}</div>
        </div>

        <div class="detail-section" v-if="currentFeedback.generated_reply">
          <h4>生成回复</h4>
          <div class="content-box reply-box">{{ currentFeedback.generated_reply }}</div>
        </div>

        <div class="detail-section" v-if="currentFeedback.keywords">
          <h4>关键词</h4>
          <div>
            <el-tag v-for="kw in currentFeedback.keywords" :key="kw" size="small" class="keyword-tag">
              {{ kw }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, Refresh } from '@element-plus/icons-vue'
import { getFeedbackList, getFeedbackDetail, batchCollectFeedback } from '@/api/feedback'

const loading = ref(false)
const collecting = ref(false)
const feedbackList = ref([])
const drawerVisible = ref(false)
const currentFeedback = ref(null)

const channelMap = { wecom: '企业微信', douyin: '抖音', email: '邮件' }
const intentMap = { inquiry: '咨询', complaint: '投诉', suggestion: '建议', praise: '表扬', other: '其他' }
const statusMap = { pending: '待处理', processing: '处理中', replied: '已回复', closed: '已关闭' }

const filters = reactive({
  channel: '',
  intent: '',
  status: '',
  dateRange: null,
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const intentTagType = (intent) => {
  const map = { inquiry: '', complaint: 'danger', suggestion: 'warning', praise: 'success', other: 'info' }
  return map[intent] || 'info'
}

const sentimentTagType = (s) => {
  const map = { '正面': 'success', '负面': 'danger', '中性': 'info' }
  return map[s] || 'info'
}

const statusTagType = (status) => {
  const map = { pending: 'warning', processing: '', replied: 'success', closed: 'info' }
  return map[status] || 'info'
}

const formatTime = (t) => t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '-'

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      channel: filters.channel || undefined,
      intent: filters.intent || undefined,
      status: filters.status || undefined,
    }
    const res = await getFeedbackList(params)
    // 后端返回的是数组
    feedbackList.value = Array.isArray(res) ? res : (res.items || res.data || [])
    pagination.total = feedbackList.value.length
  } catch (e) {
    console.error('加载反馈列表失败', e)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.channel = ''
  filters.intent = ''
  filters.status = ''
  filters.dateRange = null
  filters.keyword = ''
  pagination.page = 1
  loadData()
}

const showDetail = async (row) => {
  try {
    const res = await getFeedbackDetail(row.id)
    currentFeedback.value = res
    drawerVisible.value = true
  } catch (e) {
    currentFeedback.value = row
    drawerVisible.value = true
  }
}

const batchCollect = async () => {
  try {
    await ElMessageBox.confirm('确定要触发批量数据采集吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    collecting.value = true
    await batchCollectFeedback({})
    ElMessage.success('批量采集任务已提交')
    setTimeout(() => loadData(), 2000)
  } catch (e) {
    if (e !== 'cancel') {
      console.error('批量采集失败', e)
    }
  } finally {
    collecting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card {
  border-radius: 8px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

.action-bar {
  display: flex;
  gap: 10px;
}

.table-card {
  border-radius: 8px;
}

.pagination-area {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section h4 {
  margin-bottom: 8px;
  color: #303133;
  font-size: 14px;
}

.content-box {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
}

.reply-box {
  background: #ecf5ff;
  border: 1px solid #d9ecff;
}

.keyword-tag {
  margin: 2px 4px;
}
</style>
