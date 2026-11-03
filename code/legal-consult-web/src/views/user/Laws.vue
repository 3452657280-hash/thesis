<template>
  <div class="page-card">
    <h3 class="page-title">法条查询</h3>
    <div class="toolbar">
      <el-select v-model="query.lawName" placeholder="全部法律" clearable filterable style="width: 260px" @change="search">
        <el-option v-for="n in lawNames" :key="n" :label="n" :value="n" />
      </el-select>
      <el-input
        v-model="query.keyword"
        placeholder="输入关键字，如：工资、押金、赔偿"
        clearable
        style="width: 320px"
        :prefix-icon="Search"
        @keyup.enter="search"
        @clear="search"
      />
      <el-button type="primary" :icon="Search" @click="search">搜索</el-button>
    </div>
    <el-table :data="records" v-loading="loading" stripe border @row-click="view" class="clickable">
      <el-table-column type="index" label="#" width="60" :index="(i) => (query.page - 1) * query.size + i + 1" />
      <el-table-column prop="lawName" label="法律名称" width="220" show-overflow-tooltip />
      <el-table-column prop="chapter" label="编/章" width="180" show-overflow-tooltip />
      <el-table-column prop="articleNo" label="条号" width="140" />
      <el-table-column prop="content" label="条文内容" show-overflow-tooltip />
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click.stop="view(row)">查看全文</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="load"
        @size-change="search"
      />
    </div>

    <el-dialog v-model="visible" :title="current ? `${current.lawName} ${current.articleNo}` : ''" width="640px">
      <template v-if="current">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="法律名称">{{ current.lawName }}</el-descriptions-item>
          <el-descriptions-item label="条号">{{ current.articleNo }}</el-descriptions-item>
          <el-descriptions-item label="编/章">{{ current.chapter || '-' }}</el-descriptions-item>
          <el-descriptions-item label="施行日期">{{ current.effectiveDate || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div class="law-content">{{ current.content }}</div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { listLaws, listLawNames } from '@/api/public'
import { pageRecords, listOf } from '@/utils'

const lawNames = ref([])
const query = reactive({ keyword: '', lawName: '', page: 1, size: 10 })
const records = ref([])
const total = ref(0)
const loading = ref(false)
const visible = ref(false)
const current = ref(null)

async function load() {
  loading.value = true
  try {
    const res = pageRecords(await listLaws({ ...query, lawName: query.lawName || '' }))
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

function view(row) {
  current.value = row
  visible.value = true
}

onMounted(async () => {
  load()
  try {
    lawNames.value = listOf(await listLawNames())
  } catch {
    lawNames.value = []
  }
})
</script>

<style scoped>
.clickable :deep(.el-table__row) {
  cursor: pointer;
}
.law-content {
  margin-top: 16px;
  padding: 16px;
  background: #f7f9fb;
  border-left: 4px solid var(--law-blue);
  line-height: 1.9;
  white-space: pre-wrap;
  font-size: 15px;
}
</style>
