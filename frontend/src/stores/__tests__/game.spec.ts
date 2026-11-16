/// <reference types="vitest/jsdom" />
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useGameStore } from '../game'
import type { GameState } from '../game'

// ---------------------------------------------------------------------------
// WebSocket mock
// ---------------------------------------------------------------------------

class WsMock {
  static instance: WsMock | null = null
  static OPEN = 1
  static CONNECTING = 0
  static CLOSING = 2
  static CLOSED = 3

  readyState = WsMock.CONNECTING
  onopen: (() => void) | null = null
  onclose: (() => void) | null = null
  onmessage: ((event: { data: string }) => void) | null = null

  constructor(public url: string) {
    WsMock.instance = this
    setTimeout(() => {
      this.readyState = WsMock.OPEN
      this.onopen?.()
    }, 0)
  }

  close() {
    this.readyState = WsMock.CLOSED
    this.onclose?.()
  }

  simulateMessage(payload: unknown) {
    this.onmessage?.({ data: JSON.stringify(payload) })
  }
}

const SAMPLE_STATE: GameState = {
  turn: 1,
  result: 'in_progress',
  mothership: { row: 5, col: 3 },
  drones: [
    {
      row: 4,
      col: 3,
      heading: [0, 1],
      detection_state: 'searching',
      strategy: 'greedy_max_probability',
    },
    {
      row: 6,
      col: 4,
      heading: [1, 0],
      detection_state: 'searching',
      strategy: 'frontier_coverage',
    },
  ],
  vessel: { row: 10, col: 40 },
  detection_events: [],
  probability_map: [
    [0.5, 0.5],
    [0.5, 0.5],
  ],
}

beforeEach(() => {
  vi.useFakeTimers()
  WsMock.instance = null
  setActivePinia(createPinia())
  vi.stubGlobal('WebSocket', WsMock)
})

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------

describe('initial state', () => {
  it('status is idle', () => {
    const store = useGameStore()
    expect(store.status).toBe('idle')
  })

  it('gameState is null', () => {
    const store = useGameStore()
    expect(store.gameState).toBeNull()
  })

  it('isConnected is false', () => {
    const store = useGameStore()
    expect(store.isConnected).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// connect()
// ---------------------------------------------------------------------------

describe('connect()', () => {
  it('sets status to connecting immediately', () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    expect(store.status).toBe('connecting')
  })

  it('sets status to connected on open', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    expect(store.status).toBe('connected')
  })

  it('isConnected returns true when connected', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    expect(store.isConnected).toBe(true)
  })

  it('updates gameState on incoming message', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    WsMock.instance!.simulateMessage(SAMPLE_STATE)
    expect(store.gameState?.turn).toBe(1)
    expect(store.gameState?.mothership).toEqual({ row: 5, col: 3 })
    expect(store.gameState?.drones).toHaveLength(2)
  })

  it('gameState reflects latest message', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    WsMock.instance!.simulateMessage(SAMPLE_STATE)
    WsMock.instance!.simulateMessage({ ...SAMPLE_STATE, turn: 2 })
    expect(store.gameState?.turn).toBe(2)
  })
})

// ---------------------------------------------------------------------------
// disconnect()
// ---------------------------------------------------------------------------

describe('disconnect()', () => {
  it('sets status to disconnected', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    store.disconnect()
    expect(store.status).toBe('disconnected')
  })

  it('clears gameState on disconnect', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    WsMock.instance!.simulateMessage(SAMPLE_STATE)
    store.disconnect()
    expect(store.gameState).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// default WebSocket URL
// ---------------------------------------------------------------------------

describe('connect() without an explicit url', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
    jsdom.reconfigure({ url: 'http://localhost:3000/' })
  })

  it('uses VITE_WS_URL when it is set', () => {
    vi.stubEnv('VITE_WS_URL', 'ws://override.test/ws/game')
    useGameStore().connect()
    expect(WsMock.instance?.url).toBe('ws://override.test/ws/game')
  })

  it('derives a ws: url from the page host over http', () => {
    vi.stubEnv('VITE_WS_URL', '')
    jsdom.reconfigure({ url: 'http://triton.test:8080/' })
    useGameStore().connect()
    expect(WsMock.instance?.url).toBe('ws://triton.test:8080/ws/game')
  })

  it('derives a wss: url from the page host over https', () => {
    vi.stubEnv('VITE_WS_URL', '')
    jsdom.reconfigure({ url: 'https://triton.test/' })
    useGameStore().connect()
    expect(WsMock.instance?.url).toBe('wss://triton.test/ws/game')
  })
})
