<template>
  <div class="knowledge-base">
    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="openForm()">
        <el-icon><Plus /></el-icon>
        新增文章
      </el-button>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索知识库文章"
        clearable
        style="width: 300px"
        @keyup.enter="loadData"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="filterCategory" placeholder="全部分类" clearable style="width: 150px" @change="loadData">
        <el-option
          v-for="cat in categories"
          :key="cat.id"
          :label="cat.name"
          :value="cat.id"
        />
      </el-select>
    </div>

    <!-- 文章列表 -->
    <el-card shadow="hover" class="table-card">
      <el-table :data="articles" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容预览" show-overflow-tooltip min-width="300">
          <template #default="{ row }">
            {{ row.content?.slice(0, 100) }}{{ row.content?.length > 100 ? '...' : '' }}
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <el-tag v-for="tag in (row.tags || [])" :key="tag" size="small" class="tag-item">
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openForm(row)">编辑</el-button>
            <el-popconfirm title="确定删除此文章？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑文章' : '新增文章'"
      width="650px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="产品FAQ" value="产品FAQ" />
            <el-option label="服务流程" value="服务流程" />
            <el-option label="常见问题" value="常见问题" />
            <el-option label="政策规则" value="政策规则" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-tag
            v-for="tag in form.tags"
            :key="tag"
            closable
            class="tag-item"
            @close="removeTag(tag)"
          >{{ tag }}</el-tag>
          <el-input
            v-if="tagInputVisible"
            ref="tagInputRef"
            v-model="tagInputValue"
            size="small"
            style="width: 100px"
            @keyup.enter="addTag"
            @blur="addTag"
          />
          <el-button v-else size="small" @click="showTagInput">+ 添加标签</el-button>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="请输入文章内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  getKnowledgeList,
  createKnowledge,
  updateKnowledge,
  deleteKnowledge,
  getKnowledgeCategories
} from '@/api/knowledge'

const loading = ref(false)
const submitting = ref(false)
const articles = ref([])
const categories = ref([])
const searchKeyword = ref('')
const filterCategory = ref('')
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref(null)

const form = reactive({
  title: '',
  category: '',
  content: '',
  tags: []
})

const formRules = {
  title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }]
}

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const formatTime = (t) => t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '-'

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      category: filterCategory.value || undefined,
    }
    const res = await getKnowledgeList(params)
    articles.value = Array.isArray(res) ? res : (res.items || res.data || [])
    pagination.total = articles.value.length
  } catch (e) {
    console.error('加载知识库失败', e)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await getKnowledgeCategories()
    categories.value = res || []
  } catch (e) {
    categories.value = [
      { id: 1, name: '产品FAQ' },
      { id: 2, name: '服务流程' },
      { id: 3, name: '常见问题' },
      { id: 4, name: '政策规则' }
    ]
  }
}

const openForm = (row) => {
  if (row) {
    editingId.value = row.id
    form.title = row.title
    form.category = row.category
    form.content = row.content
    form.tags = [...(row.tags || [])]
  } else {
    editingId.value = null
    form.title = ''
    form.category = ''
    form.content = ''
    form.tags = []
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const data = { ...form }
    if (editingId.value) {
      await updateKnowledge(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createKnowledge(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error('保存失败', e)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deleteKnowledge(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    console.error('删除失败', e)
  }
}

const showTagInput = () => {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.input?.focus()
  })
}

const addTag = () => {
  const val = tagInputValue.value.trim()
  if (val && !form.tags.includes(val)) {
    form.tags.push(val)
  }
  tagInputVisible.value = false
  tagInputValue.value = ''
}

const removeTag = (tag) => {
  form.tags = form.tags.filter(t => t !== tag)
}

onMounted(() => {
  loadData()
  loadCategories()
})
</script>

<style scoped>
.knowledge-base {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-card {
  border-radius: 8px;
}

.pagination-area {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.tag-item {
  margin: 2px 4px;
}
</style>
