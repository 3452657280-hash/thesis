<template>
  <AuthShell title="账号登录">
    <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="submit">
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" clearable />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
      </el-form-item>
      <el-button type="primary" class="full" :loading="loading" @click="submit">登 录</el-button>
    </el-form>
    <div class="extra">
      还没有账号？<router-link to="/register">立即注册</router-link>
    </div>
  </AuthShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthShell from '@/components/AuthShell.vue'
import { login } from '@/api/auth'
import { useUserStore, homeOfRole } from '@/stores/user'

const store = useUserStore()
const router = useRouter()
const route = useRoute()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function submit() {
  if (!(await formRef.value.validate().catch(() => false))) return
  loading.value = true
  try {
    const data = await login(form)
    store.setLogin(data.token, data.user)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect
    let target = homeOfRole(data.user.role)
    if (typeof redirect === 'string' && redirect.startsWith('/')) {
      const need = router.resolve(redirect).matched.map((r) => r.meta.role).find(Boolean)
      if (need === data.user.role) target = redirect
    }
    router.replace(target)
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
.extra {
  margin-top: 18px;
  text-align: center;
  font-size: 14px;
  color: #909399;
}
.extra a {
  color: var(--law-blue);
  text-decoration: none;
}
</style>
