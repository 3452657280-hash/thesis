import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore, homeOfRole } from '@/stores/user'

const TopLayout = () => import('@/layouts/TopLayout.vue')
const AdminLayout = () => import('@/layouts/AdminLayout.vue')

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { title: '登录', public: true } },
  { path: '/register', component: () => import('@/views/Register.vue'), meta: { title: '注册', public: true } },
  {
    path: '/',
    component: TopLayout,
    meta: { role: 'USER' },
    redirect: '/consult',
    children: [
      { path: 'consult', component: () => import('@/views/user/Consult.vue'), meta: { title: '智能咨询', role: 'USER' } },
      { path: 'laws', component: () => import('@/views/user/Laws.vue'), meta: { title: '法条查询', role: 'USER' } },
      { path: 'templates', component: () => import('@/views/user/Templates.vue'), meta: { title: '文书模板', role: 'USER' } },
      { path: 'lawyers', component: () => import('@/views/user/Lawyers.vue'), meta: { title: '找律师', role: 'USER' } },
      { path: 'mine', component: () => import('@/views/user/Mine.vue'), meta: { title: '我的', role: 'USER' } }
    ]
  },
  {
    path: '/lawyer',
    component: TopLayout,
    meta: { role: 'LAWYER' },
    redirect: '/lawyer/profile',
    children: [
      { path: 'profile', component: () => import('@/views/lawyer/Certification.vue'), meta: { title: '资质认证', role: 'LAWYER' } },
      { path: 'appointments', component: () => import('@/views/lawyer/Appointments.vue'), meta: { title: '预约处理', role: 'LAWYER' } },
      { path: 'info', component: () => import('@/views/common/Profile.vue'), meta: { title: '个人信息', role: 'LAWYER' } }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { role: 'ADMIN' },
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '数据看板', role: 'ADMIN', icon: 'DataAnalysis' } },
      { path: 'users', component: () => import('@/views/admin/Users.vue'), meta: { title: '用户管理', role: 'ADMIN', icon: 'User' } },
      { path: 'lawyers', component: () => import('@/views/admin/LawyerAudit.vue'), meta: { title: '律师审核', role: 'ADMIN', icon: 'Stamp' } },
      { path: 'laws', component: () => import('@/views/admin/LawManage.vue'), meta: { title: '法条管理', role: 'ADMIN', icon: 'Reading' } },
      { path: 'templates', component: () => import('@/views/admin/TemplateManage.vue'), meta: { title: '文书模板管理', role: 'ADMIN', icon: 'Document' } },
      { path: 'notices', component: () => import('@/views/admin/NoticeManage.vue'), meta: { title: '公告管理', role: 'ADMIN', icon: 'Bell' } },
      { path: 'consults', component: () => import('@/views/admin/ConsultRecords.vue'), meta: { title: '咨询记录', role: 'ADMIN', icon: 'ChatLineSquare' } }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const store = useUserStore()
  if (to.meta.public) {
    if (store.isLogin) return homeOfRole(store.role)
    return true
  }
  if (!store.isLogin) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  const required = to.matched.map((r) => r.meta.role).find(Boolean)
  if (required && required !== store.role) {
    return homeOfRole(store.role)
  }
  return true
})

router.afterEach((to) => {
  const base = '法律咨询助手'
  document.title = to.meta.title ? `${to.meta.title} - ${base}` : base
})

export default router
