<script setup>
import { chatEventsApi } from '@/api/ai'
import { ref, reactive, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify' // 过滤危险的 HTML，防止 XSS 攻击
const messages = ref([
  {
    role: 'assistant',
    content:
      '您好，我是实验室助手。你可以向我提问怎么预约、取消。具体实验室信息请到【实验室列表】页查看'
  }
])
const input = ref('')
const loading = ref(false)
const listRef = ref()
const scrollToBottom = () => {
  nextTick(() => {
    const elem = listRef.value
    if (elem) elem.scrollTop = elem.scrollHeight
  })
}
const handleSend = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true

  // 先取好要发送的历史（不要包含下面即将插入的空占位）
  const history = messages.value.map(({ role, content }) => ({ role, content }))
  // 插入一条空的助手消息，边流式接收边往里填；steps 用来记录 agent 调用了哪些工具
  messages.value.push({ role: 'assistant', content: '', steps: [], thinking: true })
  const target = messages.value[messages.value.length - 1]
  scrollToBottom()

  try {
    await chatEventsApi({ messages: history }, (ev) => {
      if (ev.type === 'token') {
        target.content += ev.content
      } else if (ev.type === 'tool_call') {
        target.steps.push({ name: ev.name, args: ev.args, status: 'running', preview: '' })
      } else if (ev.type === 'tool_result') {
        const step = [...target.steps].reverse().find((s) => s.name === ev.name && s.status === 'running')
        if (step) {
          step.status = ev.ok ? 'ok' : 'error'
          step.preview = ev.preview
        } else {
          target.steps.push({ name: ev.name, args: null, status: ev.ok ? 'ok' : 'error', preview: ev.preview })
        }
      } else if (ev.type === 'error') {
        target.content = ev.message
      }
      scrollToBottom()
    })
  } catch (e) {
    console.error('流式对话失败:', e)
    if (!target.content) target.content = '（回答失败，请稍后重试）'
  } finally {
    target.thinking = false
    loading.value = false
    scrollToBottom()
  }
}
// 将 markdown 字符串转换为安全的 HTML 字符串
const parseMarkdown = (text) => {
  if (!text) return ''
  marked.setOptions({ breaks: true }) // 把 \n 转换成 <br>
  // 使用 marked 解析，然后用 DOMPurify 清理
  const rawHtml = marked.parse(text)
  return DOMPurify.sanitize(rawHtml)
}
</script>

<template>
<div>
  <el-card>
    <template #header>
      <div class="header-container">
        AI智能助手
      </div>
    </template>
    <div
      ref="listRef"
      style="
          height: 480px;
          overflow-y: auto;
          padding: 8px 4px;
          background-color: #fafafa;
          border-radius: 6px;
        "
    >
      <div
        v-for="(item, index) in messages"
        :key="index"
        :style="{
            display: 'flex',
            justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '12px'
          }"
      >
        <div
          :style="{
              maxWidth: '70%',
              padding: '10px 12px',
              borderRadius: '8px',
              backgroundColor: item.role === 'user' ? '#409eff' : '#fff',
              color: item.role === 'user' ? '#fff' : '#333',
              lineHeight: '1.6',
              boxShadow: '0 1px 2px rgba(0, 0, 0, 0.06)'
            }"
        >
          <!-- agent 工作流程：实时显示调用了哪些工具 -->
          <div v-if="item.steps && item.steps.length" class="agent-steps">
            <div class="agent-steps-title">执行过程</div>
            <div v-for="(s, i) in item.steps" :key="i" class="agent-step">
              <el-tag
                size="small"
                :type="s.status === 'running' ? 'warning' : s.status === 'ok' ? 'success' : 'danger'"
              >
                {{ s.status === 'running' ? '调用中' : s.status === 'ok' ? '已完成' : '失败' }}
              </el-tag>
              <span class="agent-step-name">{{ s.name }}</span>
              <span v-if="s.args" class="agent-step-args">{{ JSON.stringify(s.args) }}</span>
            </div>
          </div>
          <div v-html="parseMarkdown(item.content)"></div>
          <div v-if="item.thinking && !item.content" class="agent-thinking">思考中…</div>
        </div>
      </div>
    </div>

    <div style="margin-top: 12px; display: flex; gap: 8px; align-items: flex-end">
      <el-input
        v-model="input"
        type="textarea"
        :rows="2"
        placeholder="问问实验室怎么预约、开放时间..."
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.shift.stop
      ></el-input>
      <el-button type="primary" @click="handleSend" :loading="loading">发送</el-button>
    </div>
  </el-card>
</div>
</template>

<style scoped>
.header-container {
  font-weight: bold;
  font-size: 16px;
}
/* agent 执行过程 */
.agent-steps {
  margin-bottom: 8px;
  padding: 6px 8px;
  background-color: #f4f6ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  font-size: 12px;
}
.agent-steps-title {
  color: #909399;
  margin-bottom: 4px;
}
.agent-step {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 2px 0;
}
.agent-step-name {
  font-weight: bold;
  color: #303133;
}
.agent-step-args {
  color: #909399;
  word-break: break-all;
}
.agent-thinking {
  color: #909399;
  font-size: 12px;
}
</style>