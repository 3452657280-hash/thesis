<template>
  <div class="page-card" v-loading="loading">
    <h3 class="page-title">资质认证</h3>

    <el-alert v-if="!profile" type="info" show-icon :closable="false" title="您尚未提交资质认证信息，提交并审核通过后即可在「找律师」中展示并接收用户预约。" />
    <el-alert
      v-else-if="profile.auditStatus === 0"
      type="warning"
      show-icon
      :closable="false"
      title="资质审核中"
      description="您的资质信息已提交，请耐心等待管理员审核。"
    />
    <el-alert v-else-if="profile.auditStatus === 1" type="success" show-icon :closable="false" title="资质审核已通过">
      <template #default>
        您已成为平台认证律师，可在「预约处理」中查看用户预约。<span v-if="profile.auditRemark">审核意见：{{ profile.auditRemark }}</span>
      </template>
    </el-alert>
    <el-alert v-else-if="profile.auditStatus === 2" type="error" show-icon :closable="false" title="资质审核被驳回">
      <template #default>审核意见：{{ profile.auditRemark || '无' }}。请修改后重新提交。</template>
    </el-alert>

    <div class="status-row" v-if="profile">
      当前状态：
      <el-tag :type="AUDIT_STATUS[profile.auditStatus]?.type">{{ AUDIT_STATUS[profile.auditStatus]?.label }}</el-tag>
      <span class="muted" v-if="profile.createTime">提交时间：{{ formatTime(profile.createTime) }}</span>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="form">
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <el-form-item label="真实姓名" prop="realName">
            <el-input v-model="form.realName" maxlength="50" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item label="执业证号" prop="licenseNo">
            <el-input v-model="form.licenseNo" maxlength="50" placeholder="17 位律师执业证号" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item label="所在律所" prop="lawFirm">
            <el-input v-model="form.lawFirm" maxlength="100" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item label="执业年限" prop="years">
            <el-input-number v-model="form.years" :min="0" :max="60" />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="擅长领域" prop="specialtyList">
            <el-select
              v-model="form.specialtyList"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="可多选，也可输入自定义领域"
              style="width: 100%"
            >
              <el-option v-for="s in SPECIALTIES" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="个人简介" prop="intro">
            <el-input v-model="form.intro" type="textarea" :rows="5" maxlength="1000" show-word-limit />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="submit">{{ profile ? '修改并重新提交' : '提交认证' }}</el-button>
        <span class="muted tip">提交后审核状态将重置为"待审核"</span>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLawyerProfile, saveLawyerProfile } from '@/api/lawyer'
import { AUDIT_STATUS, SPECIALTIES, splitSpecialty, formatTime } from '@/utils'

const loading = ref(false)
const saving = ref(false)
const formRef = ref()
const profile = ref(null)
const form = reactive({ realName: '', licenseNo: '', lawFirm: '', years: 0, specialtyList: [], intro: '' })
const rules = {
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  licenseNo: [{ required: true, message: '请输入执业证号', trigger: 'blur' }],
  lawFirm: [{ required: true, message: '请输入所在律所', trigger: 'blur' }],
  specialtyList: [{ type: 'array', required: true, min: 1, message: '请至少选择一个擅长领域', trigger: 'change' }]
}

async function load() {
  loading.value = true
  try {
    const data = await getLawyerProfile()
    profile.value = data || null
    if (data) {
      form.realName = data.realName || ''
      form.licenseNo = data.licenseNo || ''
      form.lawFirm = data.lawFirm || ''
      form.years = data.years || 0
      form.specialtyList = splitSpecialty(data.specialty)
      form.intro = data.intro || ''
    }
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!(await formRef.value.validate().catch(() => false))) return
  if (profile.value?.auditStatus === 1) {
    const ok = await ElMessageBox.confirm('修改资质后需重新审核，审核期间将暂停展示，确定继续吗？', '提示', { type: 'warning' })
      .then(() => true)
      .catch(() => false)
    if (!ok) return
  }
  saving.value = true
  try {
    const { specialtyList, ...rest } = form
    await saveLawyerProfile({ ...rest, specialty: specialtyList.join(',') })
    ElMessage.success('提交成功，请等待审核')
    load()
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.status-row {
  margin: 16px 0 4px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}
.form {
  margin-top: 20px;
  max-width: 900px;
}
.muted {
  color: #909399;
  font-size: 13px;
}
.tip {
  margin-left: 12px;
}
</style>
