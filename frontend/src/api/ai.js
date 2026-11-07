import  request  from '../utils/request.js'
import { getToken } from '@/utils/auth.js'

export function chatApi(data){
  return request({
    url: '/api/ai/chat',
    method: 'post',
    data
  })
}

// 流式对话：每收到一段文本就回调一次 onChunk(text)
export async function chatStreamApi(data, onChunk) {
  const resp = await fetch('/api/ai/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken() || ''}`,
    },
    body: JSON.stringify(data),
  })
  if (!resp.ok || !resp.body) {
    throw new Error(`流式请求失败: ${resp.status}`)
  }
  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const text = decoder.decode(value, { stream: true })
    if (text) onChunk(text)
  }
}

// 事件流：每收到一个事件（token / tool_call / tool_result / node / error）回调一次
export async function chatEventsApi(data, onEvent) {
  const resp = await fetch('/api/ai/chat/events', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken() || ''}`,
    },
    body: JSON.stringify(data),
  })
  if (!resp.ok || !resp.body) {
    throw new Error(`流式请求失败: ${resp.status}`)
  }
  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  const flush = (line) => {
    const text = line.trim()
    if (!text) return
    try {
      onEvent(JSON.parse(text))
    } catch (e) {
      console.warn('无法解析的事件行:', text)
    }
  }
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n')) >= 0) {
      flush(buffer.slice(0, idx))
      buffer = buffer.slice(idx + 1)
    }
  }
  flush(buffer)
}