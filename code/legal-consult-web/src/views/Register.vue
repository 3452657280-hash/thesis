<template>
  <AuthShell title="注册账号">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="注册身份" prop="role">
        <el-radio-group v-model="form.role">
          <el-radio-button value="USER">咨询用户</el-radio-button>
          <el-radio-button value="LAWYER">律师</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="4~20 位字母、数字或下划线" clearable />
      </el-form-item>
      <el-form-item label="昵称" prop="nickname">
        <el-input v-model="form.nickname" placeholder="请输入昵称" clearable />
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="form.phone" placeholder="请输入手机号" clearable />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="至少 6 位" show-password />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm">
        <el-input v-model="form.confirm" type="password" placeholder="再次输入密码" show-password />
      </el-form-item>
      <el-alert
        v-if="form.role === 'LAWYER'"
        type="info"
        :closable="false"
        show-icon
        title="律师注册后请登录并提交资质认证，审核通过后才会展示给咨询用户。"
        class="tip"
      />
      <el-button type="primary" class="full" :loading="loading" @click="submit">注 册</el-button>
    </el-form>
    <div class="extra">已有账号？<router-link to="/login">返回登录</router-link></div>
  </AuthShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthShell from '@/components/AuthShell.vue'
import { register } from '@/api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ role: 'USER', username: '', nickname: '', phone: '', password: '', confirm: '' })

const rules = {
  role: [{ required: true, message: '请选择注册身份', trigger: 'change' }],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { pattern: /^\w{4,20}$/, message: '4~20 位字母、数字或下划线', trigger: 'blur' }
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [{ pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度 6~32 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, cb) => (value === form.password ? cb() : cb(new Error('两次输入的密码不一致'))),
      trigger: 'blur'
    }
  ]
}

async function submit() {
  if (!(await formRef.value.validate().catch(() => false))) return
  loading.value = true
  try {
    const { username, password, nickname, phone, role } = form
    await register({ username, password, nickname, phone, role })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.full {
  width: 100%;
  margin-top: 8px;
}
.tip {
  margin-bottom: 12px;
}
.extra {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: #909399;
}
.extra a {
  color: var(--law-blue);
  text-decoration: none;
}
:deep(.el-form-item) {
  margin-bottom: 14px;
}
</style>
