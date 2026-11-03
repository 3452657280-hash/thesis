<template>
  <div class="page-card">
    <h3 class="page-title">预约处理</h3>
    <div class="toolbar">
      <el-radio-group v-model="status" @change="load">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button v-for="(v, k) in APPOINTMENT_STATUS" :key="k" :value="Number(k)">{{ v.label }}</el-radio-button>
      </el-radio-group>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>
    <el-table :data="records" v-loading="loading" border stripe>
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="expand">
            <div class="ex-label">问题描述</div>
            <div class="ex-text">{{ row.question }}</div>
            <template v-if="row.reply">
              <div class="ex-label">我的回复</div>
              <div class="ex-text">{{ row.reply }}</div>
            </template>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="预约用户" width="130">
        <template #default="{ row }">{{ row.userNickname || row.nickname || row.username || row.userName || '-' }}</template>
      </el-table-column>
      <el-table-column label="联系电话" width="130">
        <template #default="{ row }">{{ row.userPhone || row.phone || '-' }}</template>
      </el-table-column>
      <el-table-column prop="question" label="问题描述" min-width="220" show-overflow-tooltip />
      <el-table-column label="期望时间" width="170">
        <template #default="{ row }">{{ formatTime(row.appointTime) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="APPOINTMENT_STATUS[row.status]?.type">{{ APPOINTMENT_STATUS[row.status]?.label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="提交时间" width="170">
        <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center" fixed="right">
        <template #default="{ row }">
          <template v-if="row.status === 0">
            <el-button link type="primary" @click="open(row, 1)">接受</el-button>
            <el-button link type="danger" @click="open(row, 2)">拒绝</el-button>
          </template>
          <el-button v-else-if="row.status === 1" link type="success" @click="open(row, 3)">完成并回复</el-button>
          <span v-else class="muted">—</span>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog.visible" :title="dialogTitle" width="520px">
      <div class="q-box">{{ dialog.row?.question }}</div>
      <el-form label-width="70px">
        <el-form-item label="回复" :required="dialog.status !== 1">
          <el-input
            v-model="dialog.reply"
            type="textarea"
            :rows="5"
            maxlength="2000"
            show-word-limit
            :placeholder="placeholder"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button :type="dialog.status === 2 ? 'danger' : 'primary'" :loading="dialog.loading" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { listLawyerAppointments, handleAppointment } from '@/api/lawyer'
import { APPOINTMENT_STATUS, formatTime, listOf } from '@/utils'

const status = ref('')
const records = ref([])
const loading = ref(false)
const dialog = reactive({ visible: false, loading: false, row: null, status: 1, reply: '' })

const dialogTitle = computed(() => ({ 1: '接受预约', 2: '拒绝预约', 3: '完成咨询并回复' })[dialog.status])
const placeholder = computed(
  () =>
    ({
      1: '可选，例如：已接受预约，将于约定时间电话联系您。',
      2: '请说明拒绝原因',
      3: '请填写咨询结论或法律建议'
    })[dialog.status]
)

async function load() {
  loading.value = true
  try {
    records.value = listOf(await listLawyerAppointments({ status: status.value === '' ? undefined : status.value }))
  } finally {
    loading.value = false
  }
}

function open(row, st) {
  dialog.row = row
  dialog.status = st
  dialog.reply = row.reply || ''
  dialog.visible = true
}

async function submit() {
  if (dialog.status !== 1 && !dialog.reply.trim()) {
    ElMessage.warning('请填写回复内容')
    return
  }
  dialog.loading = true
  try {
    await handleAppointment(dialog.row.id, { status: dialog.status, reply: dialog.reply.trim() })
    ElMessage.success('操作成功')
    dialog.visible = false
    load()
  } finally {
    dialog.loading = false
  }
}

onMounted(load)
</script>

<style scoped>
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
.muted {
  color: #c0c4cc;
}
.q-box {
  background: #f7f9fb;
  border-left: 4px solid var(--law-blue);
  padding: 10px 14px;
  margin-bottom: 16px;
  white-space: pre-wrap;
  line-height: 1.7;
  max-height: 160px;
  overflow: auto;
}
</style>
