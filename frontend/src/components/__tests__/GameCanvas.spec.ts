import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'

import GameCanvas from '../GameCanvas.vue'
import type { GameState } from '@/stores/game'

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

const DETECTION_GAME_STATE: GameState = {
  turn: 1,
  result: 'in_progress',
  mothership: { row: 2, col: 3 },
  drones: [
    {
      row: 5,
      col: 5,
      heading: [0, 1],
      detection_state: 'searching',
      strategy: 'greedy_max_probability',
    },
    { row: 7, col: 7, heading: [1, 0], detection_state: 'tracking', strategy: 'frontier_coverage' },
  ],
  vessel: { row: 20, col: 30 },
  detection_events: [{ drone_idx: 0, pod: 0.74 }],
  probability_map: [
    [0.5, 0.5],
    [0.5, 0.5],
  ],
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

  it('draws entities on the canvas when game state arrives', async () => {
    class CapturingMock extends WsMock {
      static instances: CapturingMock[] = []
      constructor() {
        super()
        CapturingMock.instances.push(this)
      }
    }
    CapturingMock.instances = []
    vi.stubGlobal('WebSocket', CapturingMock)
    const wrapper = mountCanvas()
    const canvas = wrapper.find('canvas').element as HTMLCanvasElement
    const ctx = canvas.getContext('2d') as CanvasRenderingContext2D
    const fillRectSpy = vi.spyOn(ctx, 'fillRect')
    const arcSpy = vi.spyOn(ctx, 'arc')

    CapturingMock.instances[0]?.onmessage?.({ data: JSON.stringify(DETECTION_GAME_STATE) })
    await nextTick()

    // fillRect: heatmap cells + BlueMothership marker; arc: drone circles + cones + detection ring
    expect(fillRectSpy).toHaveBeenCalled()
    expect(arcSpy).toHaveBeenCalled()
  })

  it('flashes the detecting drone orange in its cone color', async () => {
    class CapturingMock extends WsMock {
      static instances: CapturingMock[] = []
      constructor() {
        super()
        CapturingMock.instances.push(this)
      }
    }
    CapturingMock.instances = []
    vi.stubGlobal('WebSocket', CapturingMock)
    const wrapper = mountCanvas()
    const canvas = wrapper.find('canvas').element as HTMLCanvasElement
    const ctx = canvas.getContext('2d') as CanvasRenderingContext2D
    const fillStyles: unknown[] = []
    Object.defineProperty(ctx, 'fillStyle', {
      configurable: true,
      get: () => fillStyles[fillStyles.length - 1],
      set: (value: unknown) => {
        fillStyles.push(value)
      },
    })

    CapturingMock.instances[0]?.onmessage?.({ data: JSON.stringify(DETECTION_GAME_STATE) })
    await nextTick()

    // drone_idx 0 is in detection_events → its cone must use the orange flash color
    expect(fillStyles).toContain('rgba(255, 140, 0, 0.4)')
  })
})
