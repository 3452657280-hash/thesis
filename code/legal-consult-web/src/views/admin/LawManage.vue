<template>
  <div class="page-card">
    <h3 class="page-title">法条管理</h3>
    <div class="toolbar">
      <el-select v-model="query.lawName" placeholder="全部法律" clearable filterable style="width: 220px" @change="search">
        <el-option v-for="n in lawNames" :key="n" :label="n" :value="n" />
      </el-select>
      <el-input v-model="query.keyword" placeholder="条文关键字" clearable style="width: 240px" @keyup.enter="search" @clear="search" />
      <el-button type="primary" :icon="Search" @click="search">搜索</el-button>
      <el-button type="success" :icon="Plus" @click="openEdit()">新增法条</el-button>
    </div>
    <el-table :data="records" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="lawName" label="法律名称" width="200" show-overflow-tooltip />
      <el-table-column prop="chapter" label="编/章" width="160" show-overflow-tooltip />
      <el-table-column prop="articleNo" label="条号" width="130" />
      <el-table-column prop="content" label="条文内容" min-width="300" show-overflow-tooltip />
      <el-table-column prop="effectiveDate" label="施行日期" width="110" />
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

    <el-dialog v-model="dialog.visible" :title="dialog.form.id ? '编辑法条' : '新增法条'" width="640px">
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="90px">
        <el-form-item label="法律名称" prop="lawName">
          <el-autocomplete
            v-model="dialog.form.lawName"
            :fetch-suggestions="suggest"
            placeholder="如：中华人民共和国劳动合同法"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="编/章" prop="chapter">
          <el-input v-model="dialog.form.chapter" placeholder="如：第三章 劳动合同的履行和变更" />
        </el-form-item>
        <el-form-item label="条号" prop="articleNo">
          <el-input v-model="dialog.form.articleNo" placeholder="如：第三十条" />
        </el-form-item>
        <el-form-item label="施行日期" prop="effectiveDate">
          <el-date-picker v-model="dialog.form.effectiveDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="条文内容" prop="content">
          <el-input v-model="dialog.form.content" type="textarea" :rows="7" />
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
import { Search, Plus } from '@element-plus/icons-vue'
import { lawApi } from '@/api/admin'
import { listLawNames } from '@/api/public'
import { pageRecords, listOf } from '@/utils'

const query = reactive({ keyword: '', lawName: '', page: 1, size: 10 })
const records = ref([])
const total = ref(0)
const loading = ref(false)
const lawNames = ref([])
const formRef = ref()
const empty = () => ({ id: null, lawName: '', chapter: '', articleNo: '', effectiveDate: '', content: '' })
const dialog = reactive({ visible: false, loading: false, form: empty() })
const rules = {
  lawName: [{ required: true, message: '请输入法律名称', trigger: 'blur' }],
  articleNo: [{ required: true, message: '请输入条号', trigger: 'blur' }],
  content: [{ required: true, message: '请输入条文内容', trigger: 'blur' }]
}

async function load() {
  loading.value = true
  try {
    const res = pageRecords(await lawApi.list(query))
    records.value = res.records
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadNames() {
  try {
    lawNames.value = listOf(await listLawNames())
  } catch {
    lawNames.value = []
  }
}

function search() {
  query.page = 1
  load()
}

function suggest(q, cb) {
  cb(lawNames.value.filter((n) => !q || n.includes(q)).map((value) => ({ value })))
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
    const { id, lawName, chapter, articleNo, effectiveDate, content } = dialog.form
    const payload = { lawName, chapter, articleNo, effectiveDate: effectiveDate || null, content }
    if (id) await lawApi.update(id, payload)
    else await lawApi.create(payload)
    ElMessage.success('保存成功')
    dialog.visible = false
    load()
    loadNames()
  } finally {
    dialog.loading = false
  }
}

function remove(row) {
  ElMessageBox.confirm(`确定删除「${row.lawName} ${row.articleNo}」吗？`, '删除确认', { type: 'warning' })
    .then(async () => {
      await lawApi.remove(row.id)
      ElMessage.success('已删除')
      if (records.value.length === 1 && query.page > 1) query.page--
      load()
    })
    .catch(() => {})
}

onMounted(() => {
  load()
  loadNames()
})
</script>
