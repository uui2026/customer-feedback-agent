<template>
  <div class="ticket-list">
    <!-- 筛选栏 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :model="filters" inline class="filter-form">
        <el-form-item label="团队">
          <el-select v-model="filters.team" placeholder="全部团队" clearable style="width: 140px">
            <el-option label="客服组" value="客服组" />
            <el-option label="技术组" value="技术组" />
            <el-option label="产品组" value="产品组" />
            <el-option label="运营组" value="运营组" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="in_progress" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filters.priority" placeholder="全部优先级" clearable style="width: 140px">
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
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
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table :data="ticketList" v-loading="loading" stripe highlight-current-row style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="feedback_id" label="关联反馈" width="100">
          <template #default="{ row }">
            <el-link type="primary" :underline="false">#{{ row.feedback_id }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="team" label="团队" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ teamMap[row.team] || row.team }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="{ row }">
            <el-tag :type="priorityTagType(row.priority)" size="small" effect="dark">
              {{ priorityMap[row.priority] || row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sla_deadline" label="SLA截止" width="170">
          <template #default="{ row }">
            <span :class="slaClass(row.sla_deadline)">
              {{ formatTime(row.sla_deadline) }}
              <el-tag v-if="getSlaRemaining(row.sla_deadline) !== null" size="small" :type="getSlaTagType(row.sla_deadline)">
                {{ getSlaDisplay(row.sla_deadline) }}
              </el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assigned_to" label="负责人" width="100">
          <template #default="{ row }">
            {{ row.assigned_to || '未分配' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              @click="updateStatus(row, 'in_progress')"
            >接受</el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              type="success"
              size="small"
              @click="updateStatus(row, 'resolved')"
            >解决</el-button>
            <el-button
              v-if="row.status !== 'closed'"
              type="info"
              size="small"
              @click="updateStatus(row, 'closed')"
            >关闭</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-area">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import { ElMessage } from 'element-plus'
import { getTicketList, updateTicketStatus } from '@/api/ticket'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const loading = ref(false)
const ticketList = ref([])

const teamMap = { '客服组': '客服组', '技术组': '技术组', '产品组': '产品组', '运营组': '运营组' }
const priorityMap = { urgent: '紧急', high: '高', medium: '中', low: '低' }
const statusMap = { pending: '待处理', in_progress: '处理中', resolved: '已解决', closed: '已关闭' }

const filters = reactive({
  team: '',
  status: '',
  priority: '',
  dateRange: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const priorityTagType = (p) => {
  const map = { urgent: 'danger', high: 'warning', medium: '', low: 'info' }
  return map[p] || 'info'
}

const statusTagType = (s) => {
  const map = { pending: 'warning', in_progress: '', resolved: 'success', closed: 'info' }
  return map[s] || 'info'
}

const formatTime = (t) => t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '-'

const getSlaRemaining = (deadline) => {
  if (!deadline) return null
  const diff = dayjs(deadline).diff(dayjs(), 'hour', true)
  return diff
}

const getSlaDisplay = (deadline) => {
  const hours = getSlaRemaining(deadline)
  if (hours === null) return ''
  if (hours < 0) return '已超时'
  if (hours < 1) return `${Math.round(hours * 60)}分钟`
  return `${Math.round(hours)}小时`
}

const getSlaTagType = (deadline) => {
  const hours = getSlaRemaining(deadline)
  if (hours === null) return 'info'
  if (hours < 0) return 'danger'
  if (hours < 2) return 'warning'
  return 'success'
}

const slaClass = (deadline) => {
  const hours = getSlaRemaining(deadline)
  if (hours !== null && hours < 0) return 'sla-overdue'
  return ''
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      team: filters.team || undefined,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
    }
    const res = await getTicketList(params)
    ticketList.value = Array.isArray(res) ? res : (res.items || res.data || [])
    pagination.total = ticketList.value.length
  } catch (e) {
    console.error('加载工单列表失败', e)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.team = ''
  filters.status = ''
  filters.priority = ''
  filters.dateRange = null
  pagination.page = 1
  loadData()
}

const updateStatus = async (row, newStatus) => {
  try {
    await updateTicketStatus(row.id, newStatus)
    ElMessage.success('状态更新成功')
    row.status = newStatus
  } catch (e) {
    console.error('更新状态失败', e)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.ticket-list {
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

.table-card {
  border-radius: 8px;
}

.pagination-area {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.sla-overdue {
  color: #f56c6c;
  font-weight: 600;
}
</style>
