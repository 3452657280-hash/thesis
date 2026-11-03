<template>
  <div class="page-card">
    <h3 class="page-title">我的</h3>
    <el-tabs v-model="tab" @tab-change="onTab">
      <el-tab-pane label="个人信息" name="info">
        <ProfileForm />
      </el-tab-pane>

      <el-tab-pane label="我的预约" name="appointments">
        <div class="toolbar">
          <el-button :icon="Refresh" @click="loadAppointments">刷新</el-button>
        </div>
        <el-table :data="appointments" v-loading="apLoading" border stripe>
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="expand">
                <div class="ex-label">问题描述</div>
                <div class="ex-text">{{ row.question }}</div>
                <div class="ex-label">律师回复</div>
                <div class="ex-text">{{ row.reply || '律师暂未回复' }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="律师" width="120">
            <template #default="{ row }">{{ row.lawyerName || row.realName || '-' }}</template>
          </el-table-column>
          <el-table-column prop="question" label="问题描述" min-width="220" show-overflow-tooltip />
          <el-table-column label="期望时间" width="170">
            <template #default="{ row }">{{ formatTime(row.appointTime) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="APPOINTMENT_STATUS[row.status]?.type">{{ APPOINTMENT_STATUS[row.status]?.label || '未知' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reply" label="律师回复" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span :class="{ muted: !row.reply }">{{ row.reply || '暂未回复' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="提交时间" width="170">
            <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="我的收藏" name="favorites">
        <div v-loading="favLoading">
          <el-empty v-if="!favorites.length && !favLoading" description="还没有收藏的回答" />
          <el-card v-for="f in favorites" :key="f.messageId" shadow="never" class="fav-card">
            <div class="fav-head">
              <span class="muted">收藏于 {{ formatTime(f.createTime) }}</span>
              <div>
                <el-button link type="primary" :icon="CopyDocument" @click="copy(f.content)">复制</el-button>
                <el-button link type="danger" :icon="Delete" @click="unfavorite(f)">取消收藏</el-button>
              </div>
            </div>
            <div class="markdown-body fav-content" :class="{ collapsed: !expanded.has(f.messageId) }" v-html="renderMarkdown(f.content)" />
            <el-button link type="primary" @click="toggleExpand(f.messageId)">
              {{ expanded.has(f.messageId) ? '收起' : '展开全文' }}
            </el-button>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, CopyDocument, Delete } from '@element-plus/icons-vue'
import ProfileForm from '@/components/ProfileForm.vue'
import { myAppointments } from '@/api/appointment'
import { listFavorites, removeFavorite } from '@/api/consult'
import { formatTime, renderMarkdown, copyText, listOf, APPOINTMENT_STATUS } from '@/utils'

const route = useRoute()
const tab = ref(['info', 'appointments', 'favorites'].includes(route.query.tab) ? route.query.tab : 'info')
const appointments = ref([])
const favorites = ref([])
const apLoading = ref(false)
const favLoading = ref(false)
const expanded = ref(new Set())

async function loadAppointments() {
  apLoading.value = true
  try {
    appointments.value = listOf(await myAppointments())
  } finally {
    apLoading.value = false
  }
}

async function loadFavorites() {
  favLoading.value = true
  try {
    favorites.value = listOf(await listFavorites())
  } finally {
    favLoading.value = false
  }
}

function onTab(name) {
  if (name === 'appointments') loadAppointments()
  else if (name === 'favorites') loadFavorites()
}

function toggleExpand(id) {
  const s = new Set(expanded.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expanded.value = s
}

async function copy(text) {
  try {
    await copyText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

function unfavorite(f) {
  ElMessageBox.confirm('确定取消收藏该回答吗？', '提示', { type: 'warning' })
    .then(async () => {
      await removeFavorite(f.messageId)
      favorites.value = favorites.value.filter((x) => x.messageId !== f.messageId)
      ElMessage.success('已取消收藏')
    })
    .catch(() => {})
}

onTab(tab.value)
</script>

<style scoped>
.muted {
  color: #a8abb2;
  font-size: 13px;
}
.expand {
  padding: 8px 48px;
}
.ex-label {
  font-weight: 600;
  color: var(--law-blue);
  margin: 6px 0 4px;
}
.ex-text {
  white-space: pre-wrap;
  line-height: 1.7;
  color: #606266;
}
.fav-card {
  margin-bottom: 12px;
}
.fav-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.fav-content.collapsed {
  max-height: 120px;
  overflow: hidden;
  mask-image: linear-gradient(to bottom, #000 60%, transparent);
}
</style>
