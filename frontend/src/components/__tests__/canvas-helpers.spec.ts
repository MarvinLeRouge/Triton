import { describe, expect, it } from 'vitest'

import { cellToPixelX, cellToPixelY } from '../canvas-helpers'

describe('cellToPixelX', () => {
  it('col 0 → x 0', () => {
    expect(cellToPixelX(0, 10)).toBe(0)
  })

  it('col 1 → x equals cellSize', () => {
    expect(cellToPixelX(1, 10)).toBe(10)
  })

  it('col 5, cellSize 8 → x 40', () => {
    expect(cellToPixelX(5, 8)).toBe(40)
  })

  it('col 49, cellSize 10 → x 490', () => {
    expect(cellToPixelX(49, 10)).toBe(490)
  })
})

describe('cellToPixelY', () => {
  it('row 0 → y 0', () => {
    expect(cellToPixelY(0, 10)).toBe(0)
  })

  it('row 1 → y equals cellSize', () => {
    expect(cellToPixelY(1, 10)).toBe(10)
  })

  it('row 3, cellSize 12 → y 36', () => {
    expect(cellToPixelY(3, 12)).toBe(36)
  })

  it('row 49, cellSize 10 → y 490', () => {
    expect(cellToPixelY(49, 10)).toBe(490)
  })
})
