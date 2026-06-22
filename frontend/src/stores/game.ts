import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export type ConnectionStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

export interface Position {
  row: number
  col: number
}

export interface GameState {
  turn: number
  result: 'in_progress' | 'blue_wins' | 'red_wins'
  mothership: Position
  drones: Position[]
  vessel: Position
}

function buildWsUrl(): string {
  const envUrl = import.meta.env.VITE_WS_URL as string | undefined
  if (envUrl) return envUrl
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}/ws/game`
}

export const useGameStore = defineStore('game', () => {
  const status = ref<ConnectionStatus>('idle')
  const gameState = ref<GameState | null>(null)
  let ws: WebSocket | null = null

  const isConnected = computed(() => status.value === 'connected')

  function connect(url?: string) {
    status.value = 'connecting'
    ws = new WebSocket(url ?? buildWsUrl())

    ws.onopen = () => {
      status.value = 'connected'
    }

    ws.onclose = () => {
      status.value = 'disconnected'
      gameState.value = null
      ws = null
    }

    ws.onmessage = (event: MessageEvent) => {
      gameState.value = JSON.parse(event.data as string) as GameState
    }
  }

  function disconnect() {
    ws?.close()
  }

  return { status, gameState, isConnected, connect, disconnect }
})
