<template>
  <div class="page-card">
    <h3 class="page-title">用户管理</h3>
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="用户名 / 昵称 / 手机号" clearable style="width: 260px" @keyup.enter="search" @clear="search" />
      <el-select v-model="query.role" placeholder="全部角色" clearable style="width: 140px" @change="search">
        <el-option v-for="(v, k) in ROLE_LABEL" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="search">搜索</el-button>
    </div>
    <el-table :data="records" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="nickname" label="昵称" min-width="120" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
      <el-table-column label="角色" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="{ ADMIN: 'danger', LAWYER: 'warning', USER: 'primary' }[row.role]" effect="plain">{{ ROLE_LABEL[row.role] || row.role }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-switch
            :model-value="row.status === 1"
            :disabled="row.role === 'ADMIN'"
            @change="(v) => toggleStatus(row, v)"
          />
        </template>
      </el-table-column>
      <el-table-column label="注册时间" width="170">
        <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center">
        <template #default="{ row }">
          <el-button link type="primary" :disabled="row.role === 'ADMIN'" @click="reset(row)">重置密码</el-button>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { listUsers, updateUserStatus, resetUserPassword } from '@/api/admin'
import { pageRecords, formatTime, ROLE_LABEL } from '@/utils'

const query = reactive({ keyword: '', role: '', page: 1, size: 10 })
const records = ref([])
const total = ref(0)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = pageRecords(await listUsers(query))
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

async function toggleStatus(row, enabled) {
  const status = enabled ? 1 : 0
  const ok = await ElMessageBox.confirm(`确定${enabled ? '启用' : '禁用'}用户「${row.username}」吗？`, '提示', { type: 'warning' })
    .then(() => true)
    .catch(() => false)
  if (!ok) return
  await updateUserStatus(row.id, status)
  row.status = status
  ElMessage.success(enabled ? '已启用' : '已禁用')
}

function reset(row) {
  ElMessageBox.confirm(`确定将用户「${row.username}」的密码重置为 123456 吗？`, '重置密码', { type: 'warning' })
    .then(async () => {
      await resetUserPassword(row.id)
      ElMessage.success('密码已重置为 123456')
    })
    .catch(() => {})
}

onMounted(load)
</script>
