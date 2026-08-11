import { describe, expect, it } from 'vitest'

import {
  cellToPixelX,
  cellToPixelY,
  drawCone,
  drawHeatmapCell,
  heatmapIntensity,
} from '../canvas-helpers'

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
  fillRectArgs: number[][] = []

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
  fillRect(x: number, y: number, w: number, h: number): void {
    this.ops.push('fillRect')
    this.fillRectArgs.push([x, y, w, h])
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

// ---------------------------------------------------------------------------
// heatmapIntensity
// ---------------------------------------------------------------------------

describe('heatmapIntensity', () => {
  it('value equal to max → 1', () => {
    expect(heatmapIntensity(1, 1)).toBe(1)
  })

  it('value half of max → 0.5', () => {
    expect(heatmapIntensity(0.5, 1)).toBe(0.5)
  })

  it('value of 0 → 0', () => {
    expect(heatmapIntensity(0, 1)).toBe(0)
  })

  it('value above max is clamped to 1', () => {
    expect(heatmapIntensity(2, 1)).toBe(1)
  })

  it('max of 0 → 0 (avoids division by zero)', () => {
    expect(heatmapIntensity(0.3, 0)).toBe(0)
  })

  it('negative value is clamped to 0', () => {
    expect(heatmapIntensity(-1, 1)).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// drawHeatmapCell
// ---------------------------------------------------------------------------

describe('drawHeatmapCell', () => {
  it('intensity 0 → does not draw', () => {
    const ctx = new FakeCtx()
    drawHeatmapCell(ctx as unknown as CanvasRenderingContext2D, 10, 20, 8, 0)
    expect(ctx.ops).not.toContain('fillRect')
  })

  it('positive intensity → fills the cell rect at (x, y, size, size)', () => {
    const ctx = new FakeCtx()
    drawHeatmapCell(ctx as unknown as CanvasRenderingContext2D, 10, 20, 8, 0.5)
    expect(ctx.fillRectArgs).toEqual([[10, 20, 8, 8]])
  })

  it('higher intensity → higher alpha in fillStyle', () => {
    const lowCtx = new FakeCtx()
    drawHeatmapCell(lowCtx as unknown as CanvasRenderingContext2D, 0, 0, 8, 0.2)
    const highCtx = new FakeCtx()
    drawHeatmapCell(highCtx as unknown as CanvasRenderingContext2D, 0, 0, 8, 0.9)
    const lowAlpha = Number(lowCtx.fillStyle.match(/[\d.]+(?=\))/)?.[0])
    const highAlpha = Number(highCtx.fillStyle.match(/[\d.]+(?=\))/)?.[0])
    expect(highAlpha).toBeGreaterThan(lowAlpha)
  })
})
