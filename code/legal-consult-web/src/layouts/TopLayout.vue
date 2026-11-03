<template>
  <el-container class="top-layout">
    <el-header class="header">
      <div class="brand" @click="router.push(homeOfRole(store.role))">
        <el-icon :size="26"><ScaleIcon /></el-icon>
        <div class="brand-text">
          <div class="brand-name">法律咨询助手</div>
          <div class="brand-sub">基于Coze智能体的法律咨询系统</div>
        </div>
      </div>
      <el-menu mode="horizontal" :default-active="activeMenu" router class="nav" :ellipsis="false">
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          <el-icon><component :is="m.icon" /></el-icon>
          <span>{{ m.title }}</span>
        </el-menu-item>
      </el-menu>
      <div class="right">
        <el-popover v-if="store.role === 'USER'" placement="bottom-end" :width="360" trigger="click" @show="loadNotices">
          <template #reference>
            <el-badge :value="notices.length" :hidden="!notices.length" class="notice-badge">
              <el-button circle text><el-icon :size="18"><Bell /></el-icon></el-button>
            </el-badge>
          </template>
          <div class="notice-title">系统公告</div>
          <el-empty v-if="!notices.length" description="暂无公告" :image-size="60" />
          <el-scrollbar v-else max-height="320px">
            <div v-for="n in notices" :key="n.id" class="notice-item" @click="openNotice(n)">
              <div class="notice-name">{{ n.title }}</div>
              <div class="notice-time">{{ formatTime(n.publishTime) }}</div>
            </div>
          </el-scrollbar>
        </el-popover>
        <el-dropdown @command="onCommand">
          <span class="user">
            <el-avatar :size="30" class="avatar">{{ store.displayName.slice(0, 1) }}</el-avatar>
            <span class="uname">{{ store.displayName }}</span>
            <el-tag size="small" effect="plain">{{ ROLE_LABEL[store.role] }}</el-tag>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-main class="main">
      <router-view />
    </el-main>
    <el-dialog v-model="noticeVisible" :title="currentNotice?.title" width="560px">
      <div class="notice-content">{{ currentNotice?.content }}</div>
      <div class="notice-time">{{ formatTime(currentNotice?.publishTime) }}</div>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore, homeOfRole } from '@/stores/user'
import { listNotices } from '@/api/public'
import { ROLE_LABEL, formatTime, listOf } from '@/utils'
import ScaleIcon from '@/components/ScaleIcon.vue'

const store = useUserStore()
const route = useRoute()
const router = useRouter()

const userMenus = [
  { path: '/consult', title: '智能咨询', icon: 'ChatDotRound' },
  { path: '/laws', title: '法条查询', icon: 'Reading' },
  { path: '/templates', title: '文书模板', icon: 'Document' },
  { path: '/lawyers', title: '找律师', icon: 'Avatar' },
  { path: '/mine', title: '我的', icon: 'User' }
]
const lawyerMenus = [
  { path: '/lawyer/profile', title: '资质认证', icon: 'Stamp' },
  { path: '/lawyer/appointments', title: '预约处理', icon: 'Calendar' },
  { path: '/lawyer/info', title: '个人信息', icon: 'User' }
]

const menus = computed(() => (store.role === 'LAWYER' ? lawyerMenus : userMenus))
const activeMenu = computed(() => route.path)

const notices = ref([])
const noticeVisible = ref(false)
const currentNotice = ref(null)

async function loadNotices() {
  try {
    notices.value = listOf(await listNotices())
  } catch {
    notices.value = []
  }
}

function openNotice(n) {
  currentNotice.value = n
  noticeVisible.value = true
}

function onCommand(cmd) {
  if (cmd === 'profile') {
    router.push(store.role === 'LAWYER' ? '/lawyer/info' : '/mine')
  } else if (cmd === 'logout') {
    ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
      .then(() => {
        store.logout()
        router.replace('/login')
      })
      .catch(() => {})
  }
}

onMounted(() => {
  if (store.role === 'USER') loadNotices()
})
</script>

<style scoped>
.top-layout {
  height: 100%;
  flex-direction: column;
}
.header {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 24px;
  height: 60px;
  z-index: 10;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--law-blue);
  cursor: pointer;
  margin-right: 32px;
  flex-shrink: 0;
}
.brand-name {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
}
.brand-sub {
  font-size: 12px;
  color: #909399;
}
.nav {
  flex: 1;
  border-bottom: none;
  height: 59px;
}
.right {
  display: flex;
  align-items: center;
  gap: 16px;
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
.uname {
  font-size: 14px;
}
.main {
  flex: 1;
  overflow: auto;
  padding: 20px;
}
.notice-title {
  font-weight: 600;
  color: var(--law-blue);
  margin-bottom: 8px;
}
.notice-item {
  padding: 8px 4px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.notice-item:hover {
  background: #f5f7fa;
}
.notice-name {
  font-size: 14px;
}
.notice-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
.notice-content {
  white-space: pre-wrap;
  line-height: 1.8;
}
</style>
