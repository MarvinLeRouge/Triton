import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import GameCanvas from '../GameCanvas.vue'

class WsMock {
  static OPEN = 1
  readyState = WsMock.OPEN
  onopen: (() => void) | null = null
  onclose: (() => void) | null = null
  onmessage: ((e: { data: string }) => void) | null = null
  close() {
    this.onclose?.()
  }
  send() {}
}

beforeEach(() => {
  vi.stubGlobal('WebSocket', WsMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

function mountCanvas() {
  return mount(GameCanvas, {
    global: { plugins: [createPinia()] },
  })
}

describe('GameCanvas', () => {
  it('renders a canvas element', () => {
    const wrapper = mountCanvas()
    expect(wrapper.find('canvas').exists()).toBe(true)
  })

  it('canvas has correct dimensions', () => {
    const wrapper = mountCanvas()
    const canvas = wrapper.find('canvas').element as HTMLCanvasElement
    expect(canvas.width).toBe(500)
    expect(canvas.height).toBe(500)
  })

  it('shows status when no game state', () => {
    const wrapper = mountCanvas()
    expect(wrapper.find('.status').exists()).toBe(true)
  })

  it('calls connect on mount', () => {
    let connectUrl: string | undefined
    class TrackingConnectMock extends WsMock {
      constructor(url: string) {
        super()
        connectUrl = url
      }
    }
    vi.stubGlobal('WebSocket', TrackingConnectMock)
    mountCanvas()
    expect(connectUrl).toBeDefined()
  })

  it('calls disconnect on unmount', () => {
    let closeCalled = false
    class TrackingWsMock extends WsMock {
      close() {
        closeCalled = true
        super.close()
      }
    }
    vi.stubGlobal('WebSocket', TrackingWsMock)
    const wrapper = mountCanvas()
    wrapper.unmount()
    expect(closeCalled).toBe(true)
  })
})
