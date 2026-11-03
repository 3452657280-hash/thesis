<template>
  <el-container class="admin-layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="aside">
      <div class="logo">
        <el-icon :size="24"><ScaleIcon /></el-icon>
        <span v-show="!collapsed">法律咨询助手 · 管理端</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="collapsed"
        router
        background-color="#1f4e79"
        text-color="#c9d6e3"
        active-text-color="#ffffff"
        class="side-menu"
      >
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          <el-icon><component :is="m.meta.icon" /></el-icon>
          <template #title>{{ m.meta.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="left">
          <el-button text @click="collapsed = !collapsed">
            <el-icon :size="18"><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>管理端</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <el-dropdown @command="onCommand">
          <span class="user">
            <el-avatar :size="30" class="avatar">{{ store.displayName.slice(0, 1) }}</el-avatar>
            <span>{{ store.displayName }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import ScaleIcon from '@/components/ScaleIcon.vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const collapsed = ref(false)

const menus = computed(() => {
  const admin = router.options.routes.find((r) => r.path === '/admin')
  return (admin?.children || []).map((c) => ({ path: `/admin/${c.path}`, meta: c.meta }))
})

function onCommand(cmd) {
  if (cmd === 'logout') {
    ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
      .then(() => {
        store.logout()
        router.replace('/login')
      })
      .catch(() => {})
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100%;
}
.aside {
  background: #1f4e79;
  transition: width 0.2s;
  overflow: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-weight: 600;
  font-size: 15px;
  white-space: nowrap;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.side-menu {
  border-right: none;
}
.side-menu :deep(.el-menu-item.is-active) {
  background: #163a5b;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  height: 60px;
}
.left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}
.avatar {
  background: var(--law-blue);
}
.main {
  padding: 20px;
  overflow: auto;
}
</style>
