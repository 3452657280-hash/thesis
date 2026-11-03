import { useUserStore } from '@/stores/user'
import { handleUnauthorized } from './request'

function parseFrame(frame) {
  let event = 'message'
  const dataLines = []
  for (const rawLine of frame.split('\n')) {
    const line = rawLine.replace(/\r$/, '')
    if (!line || line.startsWith(':')) continue
    const idx = line.indexOf(':')
    const field = idx === -1 ? line : line.slice(0, idx)
    let value = idx === -1 ? '' : line.slice(idx + 1)
    if (value.startsWith(' ')) value = value.slice(1)
    if (field === 'event') event = value.trim()
    else if (field === 'data') dataLines.push(value)
  }
  if (!dataLines.length) return null
  const raw = dataLines.join('\n')
  let data
  try {
    data = JSON.parse(raw)
  } catch {
    data = { content: raw }
  }
  return { event, data }
}

export async function streamChat(sessionId, content, { onDelta, onDone, onError, signal } = {}) {
  const store = useUserStore()
  let finished = false
  const fail = (msg) => {
    if (finished) return
    finished = true
    onError && onError(msg)
  }
  let response
  try {
    response = await fetch(`/api/consult/sessions/${sessionId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        Authorization: `Bearer ${store.token}`
      },
      body: JSON.stringify({ content }),
      signal
    })
  } catch (e) {
    if (e.name === 'AbortError') return
    fail('网络异常，请稍后重试')
    return
  }

  if (response.status === 401) {
    handleUnauthorized()
    fail('登录已过期，请重新登录')
    return
  }
  if (!response.ok) {
    fail(`请求失败（${response.status}）`)
    return
  }
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    try {
      const res = await response.json()
      fail(res.msg || '请求失败')
    } catch {
      fail('请求失败')
    }
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  const dispatch = (frame) => {
    const parsed = parseFrame(frame)
    if (!parsed || finished) return
    const { event, data } = parsed
    if (event === 'delta') {
      onDelta && onDelta(data.content || '')
    } else if (event === 'done') {
      finished = true
      onDone && onDone(data)
    } else if (event === 'error') {
      fail(data.msg || '智能体响应异常')
    }
  }

  try {
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      buffer = buffer.replace(/\r\n/g, '\n')
      let sep
      while ((sep = buffer.indexOf('\n\n')) !== -1) {
        const frame = buffer.slice(0, sep)
        buffer = buffer.slice(sep + 2)
        dispatch(frame)
      }
    }
    buffer += decoder.decode()
    if (buffer.trim()) dispatch(buffer)
    if (!finished) fail('连接已断开，回答未完成')
  } catch (e) {
    if (e.name === 'AbortError') return
    fail('读取回答失败')
  }
}
