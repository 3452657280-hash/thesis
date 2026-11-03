<template>
  <div class="page-card">
    <h3 class="page-title">找律师</h3>
    <div class="toolbar">
      <span class="label">擅长领域：</span>
      <el-check-tag :checked="!query.specialty" @change="pick('')">全部</el-check-tag>
      <el-check-tag v-for="s in SPECIALTIES" :key="s" :checked="query.specialty === s" @change="pick(s)">{{ s }}</el-check-tag>
    </div>

    <div v-loading="loading">
      <el-empty v-if="!records.length && !loading" description="暂无符合条件的律师" />
      <el-row :gutter="16">
        <el-col v-for="l in records" :key="l.id" :xs="24" :sm="12" :lg="8">
          <el-card shadow="hover" class="lawyer-card">
            <div class="head">
              <el-avatar :size="56" class="avatar">{{ (l.realName || '律').slice(0, 1) }}</el-avatar>
              <div class="info">
                <div class="name">
                  {{ l.realName }} <span class="title">律师</span>
                  <el-tag size="small" type="success" effect="light"><el-icon><CircleCheck /></el-icon> 已认证</el-tag>
                </div>
                <div class="firm"><el-icon><OfficeBuilding /></el-icon>{{ l.lawFirm || '独立执业' }}</div>
                <div class="years">执业 {{ l.years || 0 }} 年</div>
              </div>
            </div>
            <div class="tags">
              <el-tag v-for="s in splitSpecialty(l.specialty)" :key="s" size="small" effect="plain">{{ s }}</el-tag>
            </div>
            <div class="intro">{{ l.intro || '暂无简介' }}</div>
            <el-button type="primary" class="full" :icon="Calendar" @click="openAppoint(l)">预约咨询</el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        layout="total, prev, pager, next"
        background
        @current-change="load"
      />
    </div>

    <el-dialog v-model="dialog.visible" :title="`预约咨询 - ${dialog.lawyer?.realName || ''} 律师`" width="520px">
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="90px">
        <el-form-item label="问题描述" prop="question">
          <el-input
            v-model="dialog.form.question"
            type="textarea"
            :rows="5"
            maxlength="2000"
            show-word-limit
            placeholder="请简要描述您的法律问题、事情经过及诉求"
          />
        </el-form-item>
        <el-form-item label="期望时间" prop="appointTime">
          <el-date-picker
            v-model="dialog.form.appointTime"
            type="datetime"
            placeholder="选择期望咨询时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="(d) => d.getTime() < Date.now() - 86400000"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="dialog.loading" @click="submit">提交预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar } from '@element-plus/icons-vue'
import { listLawyers } from '@/api/public'
import { createAppointment } from '@/api/appointment'
import { pageRecords, splitSpecialty, SPECIALTIES } from '@/utils'

const query = reactive({ specialty: '', page: 1, size: 9 })
const records = ref([])
const total = ref(0)
const loading = ref(false)
const formRef = ref()
const dialog = reactive({ visible: false, loading: false, lawyer: null, form: { question: '', appointTime: '' } })
const rules = {
  question: [
    { required: true, message: '请填写问题描述', trigger: 'blur' },
    { min: 10, message: '请至少输入 10 个字', trigger: 'blur' }
  ],
  appointTime: [{ required: true, message: '请选择期望时间', trigger: 'change' }]
}

async function load() {
  loading.value = true
  try {
    const res = pageRecords(await listLawyers(query))
    records.value = res.records
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function pick(s) {
  query.specialty = s
  query.page = 1
  load()
}

function openAppoint(l) {
  dialog.lawyer = l
  dialog.form = { question: '', appointTime: '' }
  dialog.visible = true
  formRef.value?.clearValidate()
}

async function submit() {
  if (!(await formRef.value.validate().catch(() => false))) return
  dialog.loading = true
  try {
    await createAppointment({ lawyerId: dialog.lawyer.id, ...dialog.form })
    ElMessage.success('预约已提交，可在「我的 - 我的预约」查看进度')
    dialog.visible = false
  } finally {
    dialog.loading = false
  }
}

onMounted(load)
</script>

<style scoped>
.label {
  font-size: 14px;
  color: #606266;
}
.lawyer-card {
  margin-bottom: 16px;
}
.head {
  display: flex;
  gap: 14px;
}
.avatar {
  background: var(--law-blue);
  font-size: 22px;
  flex-shrink: 0;
}
.name {
  font-size: 17px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.title {
  font-size: 13px;
  font-weight: normal;
  color: #909399;
}
.firm,
.years {
  font-size: 13px;
  color: #606266;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 12px 0 8px;
  min-height: 24px;
}
.intro {
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
  height: 42px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 12px;
}
.full {
  width: 100%;
}
</style>
