<template>
  <div class="page-card">
    <h3 class="page-title">公告管理</h3>
    <div class="toolbar">
      <el-button type="success" :icon="Plus" @click="openEdit()">发布公告</el-button>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>
    <el-table :data="records" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="content" label="内容" min-width="320" show-overflow-tooltip />
      <el-table-column label="发布时间" width="170">
        <template #default="{ row }">{{ formatTime(row.publishTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="130" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager" v-if="paged">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        layout="total, prev, pager, next"
        background
        @current-change="load"
      />
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.form.id ? '编辑公告' : '发布公告'" width="600px">
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="70px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="dialog.form.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="dialog.form.content" type="textarea" :rows="8" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="dialog.loading" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { noticeApi } from '@/api/admin'
import { formatTime } from '@/utils'

const query = reactive({ page: 1, size: 10 })
const records = ref([])
const total = ref(0)
const paged = ref(false)
const loading = ref(false)
const formRef = ref()
const empty = () => ({ id: null, title: '', content: '' })
const dialog = reactive({ visible: false, loading: false, form: empty() })
const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

async function load() {
  loading.value = true
  try {
    const data = await noticeApi.list(query)
    if (Array.isArray(data)) {
      paged.value = false
      records.value = data
      total.value = data.length
    } else {
      paged.value = true
      records.value = data?.records || []
      total.value = Number(data?.total) || 0
    }
  } finally {
    loading.value = false
  }
}

function openEdit(row) {
  dialog.form = row ? { id: row.id, title: row.title, content: row.content } : empty()
  dialog.visible = true
  formRef.value?.clearValidate()
}

async function save() {
  if (!(await formRef.value.validate().catch(() => false))) return
  dialog.loading = true
  try {
    const { id, title, content } = dialog.form
    if (id) await noticeApi.update(id, { title, content })
    else await noticeApi.create({ title, content })
    ElMessage.success('保存成功')
    dialog.visible = false
    load()
  } finally {
    dialog.loading = false
  }
}

function remove(row) {
  ElMessageBox.confirm(`确定删除公告「${row.title}」吗？`, '删除确认', { type: 'warning' })
    .then(async () => {
      await noticeApi.remove(row.id)
      ElMessage.success('已删除')
      load()
    })
    .catch(() => {})
}

onMounted(load)
</script>
