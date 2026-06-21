import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useGameStore } from '../game'

// ---------------------------------------------------------------------------
// WebSocket mock
// WsMock is defined at module level so we can access WsMock.instance from
// tests without aliasing `this` (which oxlint forbids).
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
  sentMessages: string[] = []

  constructor(public url: string) {
    WsMock.instance = this
    setTimeout(() => {
      this.readyState = WsMock.OPEN
      this.onopen?.()
    }, 0)
  }

  send(data: string) {
    this.sentMessages.push(data)
  }

  close() {
    this.readyState = WsMock.CLOSED
    this.onclose?.()
  }

  simulateMessage(payload: unknown) {
    this.onmessage?.({ data: JSON.stringify(payload) })
  }
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

  it('lastMessage is null', () => {
    const store = useGameStore()
    expect(store.lastMessage).toBeNull()
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

  it('stores incoming message in lastMessage', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    WsMock.instance!.simulateMessage({ type: 'connected' })
    expect(store.lastMessage).toEqual({ type: 'connected' })
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
})

// ---------------------------------------------------------------------------
// sendPing()
// ---------------------------------------------------------------------------

describe('sendPing()', () => {
  it('sends a ping message when connected', async () => {
    const store = useGameStore()
    store.connect('ws://localhost/ws/game')
    await vi.runAllTimersAsync()
    store.sendPing()
    expect(WsMock.instance!.sentMessages).toContain(JSON.stringify({ type: 'ping' }))
  })

  it('does nothing when not connected', () => {
    const store = useGameStore()
    expect(() => store.sendPing()).not.toThrow()
  })
})
