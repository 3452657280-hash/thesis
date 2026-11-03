<template>
  <el-row :gutter="20">
    <el-col :xs="24" :md="12">
      <el-card shadow="never" class="block">
        <template #header><span class="block-title">基本信息</span></template>
        <el-form ref="infoRef" :model="info" :rules="infoRules" label-width="80px" v-loading="loading">
          <el-form-item label="用户名">
            <el-input :model-value="me.username" disabled />
          </el-form-item>
          <el-form-item label="角色">
            <el-tag>{{ ROLE_LABEL[me.role] || me.role }}</el-tag>
          </el-form-item>
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="info.nickname" maxlength="50" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="info.phone" maxlength="20" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="info.email" maxlength="100" />
          </el-form-item>
          <el-form-item label="注册时间">
            <span class="muted">{{ formatTime(me.createTime) || '-' }}</span>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="saveInfo">保存修改</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
    <el-col :xs="24" :md="12">
      <el-card shadow="never" class="block">
        <template #header><span class="block-title">修改密码</span></template>
        <el-form ref="pwdRef" :model="pwd" :rules="pwdRules" label-width="90px">
          <el-form-item label="原密码" prop="oldPassword">
            <el-input v-model="pwd.oldPassword" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="pwd.newPassword" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirm">
            <el-input v-model="pwd.confirm" type="password" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="pwdSaving" @click="savePwd">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getMe, updateMe, updatePassword } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { ROLE_LABEL, formatTime } from '@/utils'

const store = useUserStore()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const pwdSaving = ref(false)
const infoRef = ref()
const pwdRef = ref()
const me = ref({ ...(store.user || {}) })
const info = reactive({ nickname: '', phone: '', email: '' })
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })

const infoRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [{ pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }]
}
const pwdRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度 6~32 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: (r, v, cb) => (v === pwd.newPassword ? cb() : cb(new Error('两次输入的密码不一致'))), trigger: 'blur' }
  ]
}

async function load() {
  loading.value = true
  try {
    const data = await getMe()
    me.value = data || {}
    info.nickname = data?.nickname || ''
    info.phone = data?.phone || ''
    info.email = data?.email || ''
  } finally {
    loading.value = false
  }
}

async function saveInfo() {
  if (!(await infoRef.value.validate().catch(() => false))) return
  saving.value = true
  try {
    await updateMe({ ...info })
    store.updateUser({ nickname: info.nickname })
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

async function savePwd() {
  if (!(await pwdRef.value.validate().catch(() => false))) return
  pwdSaving.value = true
  try {
    await updatePassword({ oldPassword: pwd.oldPassword, newPassword: pwd.newPassword })
    ElMessage.success('密码已修改，请重新登录')
    store.logout()
    router.replace('/login')
  } finally {
    pwdSaving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.block {
  margin-bottom: 20px;
}
.block-title {
  font-weight: 600;
  color: var(--law-blue);
}
.muted {
  color: #909399;
}
</style>
