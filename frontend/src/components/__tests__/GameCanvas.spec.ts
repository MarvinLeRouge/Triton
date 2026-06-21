import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import GameCanvas from '../GameCanvas.vue'

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

  it('displays connection status', () => {
    const wrapper = mountCanvas()
    expect(wrapper.text()).toContain('idle')
  })
})
