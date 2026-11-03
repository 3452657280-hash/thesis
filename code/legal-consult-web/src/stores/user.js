import { defineStore } from 'pinia'

const TOKEN_KEY = 'lc_token'
const USER_KEY = 'lc_user'

function readUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY)) || null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: readUser()
  }),
  getters: {
    isLogin: (state) => !!state.token,
    role: (state) => state.user?.role || '',
    displayName: (state) => state.user?.nickname || state.user?.username || ''
  },
  actions: {
    setLogin(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },
    updateUser(patch) {
      this.user = { ...(this.user || {}), ...patch }
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    }
  }
})

export function homeOfRole(role) {
  if (role === 'ADMIN') return '/admin/dashboard'
  if (role === 'LAWYER') return '/lawyer/profile'
  return '/consult'
}
