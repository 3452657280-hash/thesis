<template>
  <div class="page-card">
    <h3 class="page-title">咨询记录</h3>
    <div class="toolbar">
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>
    <el-table :data="records" v-loading="loading" border stripe>
      <el-table-column type="index" label="#" width="60" :index="(i) => (query.page - 1) * query.size + i + 1" />
      <el-table-column label="用户" width="120">
        <template #default="{ row }">{{ row.username || row.nickname || '-' }}</template>
      </el-table-column>
      <el-table-column label="问题" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">{{ questionOf(row) }}</template>
      </el-table-column>
      <el-table-column label="回答摘要" min-width="280" show-overflow-tooltip>
        <template #default="{ row }">{{ answerOf(row) }}</template>
      </el-table-column>
      <el-table-column label="耗时" width="100" align="center">
        <template #default="{ row }">{{ formatMs(row.responseMs) }}</template>
      </el-table-column>
      <el-table-column label="评分" width="150" align="center">
        <template #default="{ row }">
          <el-rate v-if="row.score" :model-value="Number(row.score)" disabled size="small" />
          <span v-else class="muted">未评价</span>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="170">
        <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="view(row)">查看</el-button>
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

    <el-drawer v-model="visible" title="问答详情" size="560px">
      <template v-if="current">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="用户">{{ current.username || current.nickname || '-' }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatTime(current.createTime) }}</el-descriptions-item>
          <el-descriptions-item label="响应耗时">{{ formatMs(current.responseMs) }}</el-descriptions-item>
          <el-descriptions-item label="首字耗时">{{ formatMs(current.firstTokenMs) }}</el-descriptions-item>
          <el-descriptions-item label="评分" :span="2">{{ current.score ? `${current.score} 星` : '未评价' }}</el-descriptions-item>
          <el-descriptions-item v-if="current.comment" label="评论" :span="2">{{ current.comment }}</el-descriptions-item>
        </el-descriptions>
        <div class="sec-title">用户问题</div>
        <div class="q-box">{{ questionOf(current) }}</div>
        <div class="sec-title">智能体回答</div>
        <div class="a-box markdown-body" v-html="renderMarkdown(fullAnswerOf(current))" />
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listConsults } from '@/api/admin'
import { pageRecords, formatTime, formatMs, renderMarkdown } from '@/utils'

const query = reactive({ page: 1, size: 10 })
const records = ref([])
const total = ref(0)
const loading = ref(false)
const visible = ref(false)
const current = ref(null)

const questionOf = (r) => r.question || r.questionContent || r.userContent || ''
const answerOf = (r) => r.answerSummary || r.answer || r.answerContent || r.content || ''
const fullAnswerOf = (r) => r.answer || r.answerContent || r.content || r.answerSummary || ''

async function load() {
  loading.value = true
  try {
    const res = pageRecords(await listConsults(query))
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

onMounted(load)
</script>

<style scoped>
.muted {
  color: #c0c4cc;
  font-size: 13px;
}
.sec-title {
  font-weight: 600;
  color: var(--law-blue);
  margin: 18px 0 8px;
}
.q-box {
  background: #f7f9fb;
  border-left: 4px solid var(--law-blue);
  padding: 10px 14px;
  white-space: pre-wrap;
  line-height: 1.7;
}
.a-box {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px 14px;
}
</style>
