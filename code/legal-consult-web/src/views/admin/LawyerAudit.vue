<template>
  <div class="page-card">
    <h3 class="page-title">律师审核</h3>
    <div class="toolbar">
      <el-radio-group v-model="auditStatus" @change="load">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button v-for="(v, k) in AUDIT_STATUS" :key="k" :value="Number(k)">{{ v.label }}</el-radio-button>
      </el-radio-group>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>
    <el-table :data="records" v-loading="loading" border stripe>
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="expand">
            <div class="ex-label">个人简介</div>
            <div class="ex-text">{{ row.intro || '无' }}</div>
            <template v-if="row.auditRemark">
              <div class="ex-label">审核意见</div>
              <div class="ex-text">{{ row.auditRemark }}</div>
            </template>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="realName" label="真实姓名" width="110" />
      <el-table-column label="账号" width="120">
        <template #default="{ row }">{{ row.username || row.userId }}</template>
      </el-table-column>
      <el-table-column prop="licenseNo" label="执业证号" width="190" />
      <el-table-column prop="lawFirm" label="所在律所" min-width="160" show-overflow-tooltip />
      <el-table-column label="擅长领域" min-width="180">
        <template #default="{ row }">
          <el-tag v-for="s in splitSpecialty(row.specialty)" :key="s" size="small" effect="plain" class="sp-tag">{{ s }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="years" label="执业年限" width="90" align="center" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="AUDIT_STATUS[row.auditStatus]?.type">{{ AUDIT_STATUS[row.auditStatus]?.label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="提交时间" width="170">
        <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" :disabled="row.auditStatus === 1" @click="open(row, 1)">通过</el-button>
          <el-button link type="danger" :disabled="row.auditStatus === 2" @click="open(row, 2)">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog.visible" :title="dialog.status === 1 ? '审核通过' : '驳回申请'" width="480px">
      <p class="who">律师：{{ dialog.row?.realName }}（{{ dialog.row?.licenseNo }}）</p>
      <el-input
        v-model="dialog.remark"
        type="textarea"
        :rows="4"
        maxlength="255"
        show-word-limit
        :placeholder="dialog.status === 1 ? '审核意见（可选）' : '请填写驳回原因'"
      />
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button :type="dialog.status === 1 ? 'success' : 'danger'" :loading="dialog.loading" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { listLawyerAudits, auditLawyer } from '@/api/admin'
import { AUDIT_STATUS, splitSpecialty, formatTime, listOf } from '@/utils'

const auditStatus = ref(0)
const records = ref([])
const loading = ref(false)
const dialog = reactive({ visible: false, loading: false, row: null, status: 1, remark: '' })

async function load() {
  loading.value = true
  try {
    records.value = listOf(await listLawyerAudits({ auditStatus: auditStatus.value === '' ? undefined : auditStatus.value }))
  } finally {
    loading.value = false
  }
}

function open(row, status) {
  dialog.row = row
  dialog.status = status
  dialog.remark = status === 1 ? '资质审核通过' : ''
  dialog.visible = true
}

async function submit() {
  if (dialog.status === 2 && !dialog.remark.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  dialog.loading = true
  try {
    await auditLawyer(dialog.row.id, { auditStatus: dialog.status, auditRemark: dialog.remark.trim() })
    ElMessage.success('审核完成')
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
.sp-tag {
  margin: 2px 4px 2px 0;
}
.who {
  margin: 0 0 12px;
  color: #606266;
}
</style>
