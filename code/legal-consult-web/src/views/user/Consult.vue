<template>
  <div class="consult">
    <aside class="sessions">
      <el-button type="primary" class="new-btn" :icon="Plus" @click="newSession">新建咨询</el-button>
      <el-scrollbar class="session-list" v-loading="sessionLoading">
        <el-empty v-if="!sessions.length && !sessionLoading" description="暂无会话" :image-size="70" />
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === currentId }"
          @click="switchSession(s.id)"
        >
          <el-icon class="s-icon"><ChatLineRound /></el-icon>
          <div class="s-body">
            <div class="s-title" :title="s.title">{{ s.title || '新的咨询' }}</div>
            <div class="s-time">{{ formatTime(s.updateTime || s.createTime) }}</div>
          </div>
          <el-dropdown trigger="click" @command="(cmd) => onSessionCommand(cmd, s)" @click.stop>
            <el-icon class="s-more" @click.stop><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="rename" :icon="Edit">重命名</el-dropdown-item>
                <el-dropdown-item command="delete" :icon="Delete">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-scrollbar>
    </aside>

    <section class="chat">
      <div class="disclaimer">
        <el-icon><WarningFilled /></el-icon>
        本系统回答由AI智能体生成，仅供参考，不构成正式法律意见。
      </div>

      <div ref="scrollRef" class="messages" v-loading="messageLoading">
        <div v-if="!messages.length && !messageLoading" class="welcome">
          <el-icon :size="48" color="#1f4e79"><ScaleIcon /></el-icon>
          <h2>您好，我是法律咨询助手</h2>
          <p>请描述您遇到的法律问题，我会结合相关法律法规为您提供参考建议。</p>
        </div>

        <div v-for="(m, idx) in messages" :key="m.id || `tmp-${idx}`" class="msg" :class="m.role">
          <el-avatar :size="36" class="msg-avatar" :class="m.role">
            <template v-if="m.role === 'user'">{{ store.displayName.slice(0, 1) }}</template>
            <el-icon v-else :size="20"><ScaleIcon /></el-icon>
          </el-avatar>
          <div class="msg-main">
            <div class="bubble">
              <div v-if="m.role === 'user'" class="user-text">{{ m.content }}</div>
              <template v-else>
                <div v-if="m.streaming && !m.content" class="thinking">
                  <span class="dot" /><span class="dot" /><span class="dot" />正在思考…
                </div>
                <div v-else class="markdown-body" :class="{ streaming: m.streaming }" v-html="renderMarkdown(m.content)" />
              </template>
            </div>
            <div v-if="m.role === 'assistant' && !m.streaming && m.id" class="msg-actions">
              <el-tooltip content="复制" placement="top">
                <el-button text size="small" :icon="CopyDocument" @click="copy(m)">复制</el-button>
              </el-tooltip>
              <el-button
                text
                size="small"
                :type="favoriteIds.has(m.id) ? 'warning' : ''"
                :icon="favoriteIds.has(m.id) ? StarFilled : Star"
                @click="toggleFavorite(m)"
              >
                {{ favoriteIds.has(m.id) ? '已收藏' : '收藏' }}
              </el-button>
              <el-button text size="small" :icon="ChatDotSquare" @click="openFeedback(m)">
                {{ m.feedbackScore ? `已评价 ${m.feedbackScore} 星` : '评价' }}
              </el-button>
              <span v-if="m.responseMs" class="meta">耗时 {{ formatMs(m.responseMs) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="composer">
        <div class="examples">
          <span class="ex-label">试试问：</span>
          <el-button
            v-for="q in examples"
            :key="q"
            size="small"
            round
            :disabled="generating"
            @click="send(q)"
          >
            {{ q }}
          </el-button>
        </div>
        <div class="input-row">
          <el-input
            v-model="input"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 6 }"
            resize="none"
            maxlength="2000"
            placeholder="请输入您的法律问题，Enter 发送，Shift+Enter 换行"
            @keydown.enter.exact.prevent="send()"
          />
          <div class="btns">
            <el-button v-if="generating" type="danger" plain :icon="VideoPause" @click="stop">停止</el-button>
            <el-button type="primary" :icon="Promotion" :loading="generating" :disabled="generating || !input.trim()" @click="send()">
              {{ generating ? '正在思考…' : '发送' }}
            </el-button>
          </div>
        </div>
      </div>
    </section>

    <el-dialog v-model="feedback.visible" title="评价本条回答" width="440px">
      <el-form label-width="70px">
        <el-form-item label="评分">
          <el-rate v-model="feedback.score" show-text :texts="['很差', '较差', '一般', '满意', '非常满意']" />
        </el-form-item>
        <el-form-item label="评论">
          <el-input v-model="feedback.comment" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="可选，说说您的看法" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="feedback.visible = false">取消</el-button>
        <el-button type="primary" :loading="feedback.loading" @click="submitFeedback">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  CopyDocument,
  Star,
  StarFilled,
  ChatDotSquare,
  Promotion,
  VideoPause
} from '@element-plus/icons-vue'
import ScaleIcon from '@/components/ScaleIcon.vue'
import { useUserStore } from '@/stores/user'
import {
  listSessions,
  createSession,
  renameSession,
  deleteSession,
  listMessages,
  listFavorites,
  addFavorite,
  removeFavorite,
  sendFeedback
} from '@/api/consult'
import { streamChat } from '@/api/chat'
import { renderMarkdown, formatTime, formatMs, copyText, listOf } from '@/utils'

const store = useUserStore()
const examples = ['公司拖欠工资三个月怎么办？', '网购买到假货可以要求几倍赔偿？', '租房押金房东不退怎么处理？', '今天天气怎么样？']

const sessions = ref([])
const currentId = ref(null)
const messages = ref([])
const favoriteIds = ref(new Set())
const input = ref('')
const generating = ref(false)
const sessionLoading = ref(false)
const messageLoading = ref(false)
const scrollRef = ref()
let controller = null

const feedback = reactive({ visible: false, score: 5, comment: '', message: null, loading: false })

function scrollToBottom() {
  nextTick(() => {
    const el = scrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function loadSessions() {
  sessionLoading.value = true
  try {
    sessions.value = listOf(await listSessions())
  } finally {
    sessionLoading.value = false
  }
}

async function loadFavorites() {
  try {
    const list = listOf(await listFavorites())
    favoriteIds.value = new Set(list.map((f) => f.messageId))
  } catch {
    favoriteIds.value = new Set()
  }
}

async function loadMessages(id) {
  messageLoading.value = true
  try {
    const list = listOf(await listMessages(id))
    if (currentId.value === id) {
      messages.value = list
      scrollToBottom()
    }
  } catch {
    messages.value = []
  } finally {
    messageLoading.value = false
  }
}

function switchSession(id) {
  if (id === currentId.value) return
  if (generating.value) {
    ElMessage.warning('回答生成中，请稍候或先停止生成')
    return
  }
  currentId.value = id
  messages.value = []
  loadMessages(id)
}

async function newSession() {
  if (generating.value) {
    ElMessage.warning('回答生成中，请稍候')
    return null
  }
  const s = await createSession()
  sessions.value.unshift({ ...s, title: s.title || '新的咨询' })
  currentId.value = s.id
  messages.value = []
  return s
}

function onSessionCommand(cmd, s) {
  if (cmd === 'rename') {
    ElMessageBox.prompt('请输入新的会话标题', '重命名', {
      inputValue: s.title,
      inputValidator: (v) => (!!v && v.trim().length > 0 && v.trim().length <= 100) || '标题长度 1~100 个字符'
    })
      .then(async ({ value }) => {
        await renameSession(s.id, value.trim())
        s.title = value.trim()
        ElMessage.success('已重命名')
      })
      .catch(() => {})
  } else if (cmd === 'delete') {
    if (generating.value && s.id === currentId.value) {
      ElMessage.warning('回答生成中，无法删除当前会话')
      return
    }
    ElMessageBox.confirm(`确定删除会话「${s.title}」吗？会话中的所有消息将一并删除。`, '删除确认', { type: 'warning' })
      .then(async () => {
        await deleteSession(s.id)
        sessions.value = sessions.value.filter((x) => x.id !== s.id)
        if (currentId.value === s.id) {
          currentId.value = null
          messages.value = []
          if (sessions.value.length) switchSession(sessions.value[0].id)
        }
        ElMessage.success('已删除')
      })
      .catch(() => {})
  }
}

async function send(text) {
  const content = (text ?? input.value).trim()
  if (!content || generating.value) return
  if (!currentId.value) {
    try {
      const s = await newSession()
      if (!s) return
    } catch {
      return
    }
  }
  const sessionId = currentId.value
  if (text === undefined) input.value = ''

  messages.value.push({ role: 'user', content })
  const answer = reactive({ role: 'assistant', content: '', streaming: true })
  messages.value.push(answer)
  const userMsg = messages.value[messages.value.length - 2]
  generating.value = true
  scrollToBottom()

  controller = new AbortController()
  await streamChat(sessionId, content, {
    signal: controller.signal,
    onDelta(delta) {
      answer.content += delta
      scrollToBottom()
    },
    onDone(data) {
      answer.id = data.messageId
      answer.responseMs = data.responseMs
      answer.firstTokenMs = data.firstTokenMs
      answer.streaming = false
      if (data.userMessageId) userMsg.id = data.userMessageId
    },
    onError(msg) {
      ElMessage.error(msg)
      answer.streaming = false
      if (!answer.content) answer.content = '> 抱歉，本次回答生成失败，请稍后重试。'
    }
  })
  answer.streaming = false
  generating.value = false
  controller = null
  scrollToBottom()
  refreshSessionTitle(sessionId)
}

async function refreshSessionTitle(sessionId) {
  try {
    const list = listOf(await listSessions())
    const keepCurrent = currentId.value
    sessions.value = list
    currentId.value = keepCurrent
  } catch {
    const s = sessions.value.find((x) => x.id === sessionId)
    if (s) sessions.value = [s, ...sessions.value.filter((x) => x.id !== sessionId)]
  }
}

function stop() {
  if (controller) {
    controller.abort()
    ElMessage.info('已停止生成')
  }
}

async function copy(m) {
  try {
    await copyText(m.content)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

async function toggleFavorite(m) {
  const set = new Set(favoriteIds.value)
  if (set.has(m.id)) {
    await removeFavorite(m.id)
    set.delete(m.id)
    ElMessage.success('已取消收藏')
  } else {
    await addFavorite(m.id)
    set.add(m.id)
    ElMessage.success('收藏成功')
  }
  favoriteIds.value = set
}

function openFeedback(m) {
  feedback.message = m
  feedback.score = m.feedbackScore || 5
  feedback.comment = ''
  feedback.visible = true
}

async function submitFeedback() {
  if (!feedback.score) {
    ElMessage.warning('请选择评分')
    return
  }
  feedback.loading = true
  try {
    await sendFeedback(feedback.message.id, { score: feedback.score, comment: feedback.comment })
    feedback.message.feedbackScore = feedback.score
    feedback.visible = false
    ElMessage.success('感谢您的评价')
  } finally {
    feedback.loading = false
  }
}

onMounted(async () => {
  loadFavorites()
  await loadSessions()
  if (sessions.value.length) {
    currentId.value = sessions.value[0].id
    loadMessages(currentId.value)
  }
})

onBeforeUnmount(() => {
  if (controller) controller.abort()
})
</script>

<style scoped>
.consult {
  display: flex;
  height: calc(100vh - 100px);
  min-height: 520px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.06);
  overflow: hidden;
}
.sessions {
  width: 260px;
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  background: #fafbfc;
}
.new-btn {
  margin: 14px;
}
.session-list {
  flex: 1;
  padding: 0 8px 8px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.15s;
}
.session-item:hover {
  background: #eef2f6;
}
.session-item.active {
  background: #e3ebf3;
}
.session-item.active .s-title {
  color: var(--law-blue);
  font-weight: 600;
}
.s-icon {
  color: #909399;
  flex-shrink: 0;
}
.s-body {
  flex: 1;
  min-width: 0;
}
.s-title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.s-time {
  font-size: 12px;
  color: #a8abb2;
  margin-top: 2px;
}
.s-more {
  color: #909399;
  padding: 4px;
  visibility: hidden;
}
.session-item:hover .s-more,
.session-item.active .s-more {
  visibility: visible;
}
.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.disclaimer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 13px;
  color: #b88230;
  background: #fdf6ec;
  border-bottom: 1px solid #faecd8;
  flex-shrink: 0;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  background: #f7f9fb;
}
.welcome {
  text-align: center;
  color: #606266;
  margin-top: 8vh;
}
.welcome h2 {
  color: var(--law-blue);
  margin: 12px 0 8px;
}
.msg {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
.msg.user {
  flex-direction: row-reverse;
}
.msg-avatar {
  flex-shrink: 0;
}
.msg-avatar.user {
  background: #8fa7bc;
}
.msg-avatar.assistant {
  background: var(--law-blue);
}
.msg-main {
  max-width: 78%;
  display: flex;
  flex-direction: column;
}
.msg.user .msg-main {
  align-items: flex-end;
}
.bubble {
  padding: 10px 14px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #ebeef5;
}
.msg.user .bubble {
  background: var(--law-blue);
  color: #fff;
  border-color: var(--law-blue);
}
.user-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
  font-size: 14px;
}
.markdown-body.streaming::after {
  content: '▍';
  color: var(--law-blue);
  animation: blink 1s steps(1) infinite;
}
.thinking {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 14px;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--law-blue);
  animation: bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2) {
  animation-delay: 0.15s;
}
.dot:nth-child(3) {
  animation-delay: 0.3s;
  margin-right: 6px;
}
.msg-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 4px;
}
.msg-actions .el-button {
  margin-left: 0;
}
.meta {
  font-size: 12px;
  color: #a8abb2;
  margin-left: 8px;
}
.composer {
  border-top: 1px solid #ebeef5;
  padding: 10px 16px 14px;
  flex-shrink: 0;
}
.examples {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}
.examples .el-button {
  margin-left: 0;
}
.ex-label {
  font-size: 13px;
  color: #909399;
}
.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
.btns {
  display: flex;
  gap: 8px;
}
.btns .el-button {
  margin-left: 0;
}
@keyframes blink {
  50% {
    opacity: 0;
  }
}
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
