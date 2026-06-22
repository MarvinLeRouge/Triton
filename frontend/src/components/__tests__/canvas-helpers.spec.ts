import { describe, expect, it } from 'vitest'

import { cellToPixelX, cellToPixelY, drawCone } from '../canvas-helpers'

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

// ---------------------------------------------------------------------------
// drawCone
// ---------------------------------------------------------------------------

class FakeCtx {
  ops: string[] = []
  fillStyle = ''

  beginPath(): void {
    this.ops.push('beginPath')
  }
  moveTo(_x: number, _y: number): void {
    this.ops.push('moveTo')
  }
  arc(_x: number, _y: number, _r: number, _s: number, _e: number): void {
    this.ops.push('arc')
  }
  closePath(): void {
    this.ops.push('closePath')
  }
  fill(): void {
    this.ops.push('fill')
  }
}

describe('drawCone', () => {
  it('calls canvas ops in order: beginPath → moveTo → arc → closePath → fill', () => {
    const ctx = new FakeCtx()
    drawCone(ctx as unknown as CanvasRenderingContext2D, 100, 100, 0, 1, 60, 80, 'blue')
    expect(ctx.ops).toEqual(['beginPath', 'moveTo', 'arc', 'closePath', 'fill'])
  })

  it('sets fillStyle to the provided color', () => {
    const ctx = new FakeCtx()
    drawCone(ctx as unknown as CanvasRenderingContext2D, 50, 50, 1, 0, 60, 40, 'rgba(255,0,0,0.5)')
    expect(ctx.fillStyle).toBe('rgba(255,0,0,0.5)')
  })

  it('east heading (drow=0, dcol=1) runs without error', () => {
    const ctx = new FakeCtx()
    drawCone(ctx as unknown as CanvasRenderingContext2D, 0, 0, 0, 1, 60, 10, 'blue')
    expect(ctx.ops).toContain('arc')
  })

  it('south heading (drow=1, dcol=0) runs without error', () => {
    const ctx = new FakeCtx()
    drawCone(ctx as unknown as CanvasRenderingContext2D, 0, 0, 1, 0, 60, 10, 'blue')
    expect(ctx.ops).toContain('arc')
  })
})
