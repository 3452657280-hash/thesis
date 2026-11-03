<template>
  <div class="page-card">
    <h3 class="page-title">文书模板管理</h3>
    <div class="toolbar">
      <el-select v-model="query.category" placeholder="全部分类" clearable style="width: 160px" @change="search">
        <el-option v-for="c in TEMPLATE_CATEGORIES" :key="c" :label="c" :value="c" />
      </el-select>
      <el-button type="success" :icon="Plus" @click="openEdit()">新增模板</el-button>
    </div>
    <el-table :data="records" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="模板名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="110" />
      <el-table-column prop="description" label="说明" min-width="220" show-overflow-tooltip />
      <el-table-column prop="fileUrl" label="文件地址" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <el-link type="primary" :href="row.fileUrl" target="_blank">{{ row.fileUrl }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="downloadCount" label="下载次数" width="90" align="center" />
      <el-table-column label="创建时间" width="170">
        <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="130" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="search"
      />
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.form.id ? '编辑模板' : '新增模板'" width="580px">
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="90px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="dialog.form.name" maxlength="100" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="dialog.form.category" filterable allow-create style="width: 100%">
            <el-option v-for="c in TEMPLATE_CATEGORIES" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件地址" prop="fileUrl">
          <el-input v-model="dialog.form.fileUrl" placeholder="外链地址或 /files/xxx.docx" />
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="dialog.form.description" type="textarea" :rows="4" maxlength="500" show-word-limit />
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
import { Plus } from '@element-plus/icons-vue'
import { templateApi } from '@/api/admin'
import { pageRecords, formatTime, TEMPLATE_CATEGORIES } from '@/utils'

const query = reactive({ category: '', page: 1, size: 10 })
const records = ref([])
const total = ref(0)
const loading = ref(false)
const formRef = ref()
const empty = () => ({ id: null, name: '', category: '', fileUrl: '', description: '' })
const dialog = reactive({ visible: false, loading: false, form: empty() })
const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  fileUrl: [{ required: true, message: '请输入文件地址', trigger: 'blur' }]
}

async function load() {
  loading.value = true
  try {
    const res = pageRecords(await templateApi.list(query))
    records.value = res.records
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function search() {
  query.page = 1
  load()
}

function openEdit(row) {
  dialog.form = row ? { ...empty(), ...row } : empty()
  dialog.visible = true
  formRef.value?.clearValidate()
}

async function save() {
  if (!(await formRef.value.validate().catch(() => false))) return
  dialog.loading = true
  try {
    const { id, name, category, fileUrl, description } = dialog.form
    const payload = { name, category, fileUrl, description }
    if (id) await templateApi.update(id, payload)
    else await templateApi.create(payload)
    ElMessage.success('保存成功')
    dialog.visible = false
    load()
  } finally {
    dialog.loading = false
  }
}

function remove(row) {
  ElMessageBox.confirm(`确定删除模板「${row.name}」吗？`, '删除确认', { type: 'warning' })
    .then(async () => {
      await templateApi.remove(row.id)
      ElMessage.success('已删除')
      if (records.value.length === 1 && query.page > 1) query.page--
      load()
    })
    .catch(() => {})
}

onMounted(load)
</script>
