import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export type ConnectionStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

export const useGameStore = defineStore('game', () => {
  const status = ref<ConnectionStatus>('idle')
  const lastMessage = ref<unknown>(null)
  let ws: WebSocket | null = null

  const isConnected = computed(() => status.value === 'connected')

  function connect(url: string) {
    status.value = 'connecting'
    ws = new WebSocket(url)

    ws.onopen = () => {
      status.value = 'connected'
    }

    ws.onclose = () => {
      status.value = 'disconnected'
      ws = null
    }

    ws.onmessage = (event: MessageEvent) => {
      lastMessage.value = JSON.parse(event.data as string)
    }
  }

  function disconnect() {
    ws?.close()
  }

  function sendPing() {
    if (ws !== null && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }

  return { status, lastMessage, isConnected, connect, disconnect, sendPing }
})
