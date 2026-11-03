import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  typographer: false
})

const defaultLinkOpen =
  md.renderer.rules.link_open ||
  ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))

md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  tokens[idx].attrSet('target', '_blank')
  tokens[idx].attrSet('rel', 'noopener noreferrer')
  return defaultLinkOpen(tokens, idx, options, env, self)
}

export function renderMarkdown(text) {
  return md.render(text || '')
}

export function formatTime(value) {
  if (!value) return ''
  if (typeof value === 'string') return value.replace('T', ' ').slice(0, 19)
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

export function formatMs(ms) {
  if (ms === null || ms === undefined || ms === '') return '-'
  const n = Number(ms)
  if (Number.isNaN(n)) return '-'
  return n >= 1000 ? `${(n / 1000).toFixed(2)} s` : `${n} ms`
}

export function pageRecords(data) {
  if (!data) return { records: [], total: 0 }
  if (Array.isArray(data)) return { records: data, total: data.length }
  return { records: data.records || [], total: Number(data.total) || 0 }
}

export function listOf(data) {
  if (!data) return []
  if (Array.isArray(data)) return data
  return data.records || []
}

export function splitSpecialty(s) {
  if (!s) return []
  return String(s)
    .split(/[,，、;；\s]+/)
    .map((x) => x.trim())
    .filter(Boolean)
}

export async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text)
    return
  }
  const ta = document.createElement('textarea')
  ta.value = text
  ta.style.position = 'fixed'
  ta.style.opacity = '0'
  document.body.appendChild(ta)
  ta.select()
  document.execCommand('copy')
  document.body.removeChild(ta)
}

export const APPOINTMENT_STATUS = {
  0: { label: '待处理', type: 'warning' },
  1: { label: '已接受', type: 'primary' },
  2: { label: '已拒绝', type: 'danger' },
  3: { label: '已完成', type: 'success' }
}

export const AUDIT_STATUS = {
  0: { label: '待审核', type: 'warning' },
  1: { label: '已通过', type: 'success' },
  2: { label: '已驳回', type: 'danger' }
}

export const ROLE_LABEL = {
  USER: '咨询用户',
  LAWYER: '律师',
  ADMIN: '管理员'
}

export const SPECIALTIES = ['劳动纠纷', '合同纠纷', '婚姻家庭', '消费维权', '交通事故', '房产纠纷', '刑事辩护', '公司法务', '知识产权']

export const TEMPLATE_CATEGORIES = ['劳动', '合同', '婚姻家庭', '消费维权', '交通事故']
