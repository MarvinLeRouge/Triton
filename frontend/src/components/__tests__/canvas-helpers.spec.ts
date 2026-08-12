import { describe, expect, it } from 'vitest'

import {
  cellToPixelX,
  cellToPixelY,
  detectionStateColor,
  drawCone,
  drawDetectionRing,
  drawDroneMarker,
  drawGrid,
  drawHeatmap,
  drawHeatmapCell,
  drawMothershipMarker,
  drawStrategyLabel,
  drawVesselMarker,
  heatmapIntensity,
  strategyLabel,
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
  strokeStyle = ''
  lineWidth = 0
  font = ''
  textAlign = ''
  fillRectArgs: number[][] = []
  fillTextArgs: [string, number, number][] = []

  beginPath(): void {
    this.ops.push('beginPath')
  }
  moveTo(_x: number, _y: number): void {
    this.ops.push('moveTo')
  }
  lineTo(_x: number, _y: number): void {
    this.ops.push('lineTo')
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
  stroke(): void {
    this.ops.push('stroke')
  }
  fillText(text: string, x: number, y: number): void {
    this.ops.push('fillText')
    this.fillTextArgs.push([text, x, y])
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

// ---------------------------------------------------------------------------
// detectionStateColor
// ---------------------------------------------------------------------------

describe('detectionStateColor', () => {
  it('searching → transparent', () => {
    expect(detectionStateColor('searching')).toBe('transparent')
  })

  it('signaling → a color', () => {
    expect(detectionStateColor('signaling')).not.toBe('transparent')
  })

  it('confirming → a color', () => {
    expect(detectionStateColor('confirming')).not.toBe('transparent')
  })

  it('tracking → a color', () => {
    expect(detectionStateColor('tracking')).not.toBe('transparent')
  })

  it('unknown state → transparent', () => {
    expect(detectionStateColor('unknown')).toBe('transparent')
  })
})

// ---------------------------------------------------------------------------
// strategyLabel
// ---------------------------------------------------------------------------

describe('strategyLabel', () => {
  it('greedy_max_probability → GMP', () => {
    expect(strategyLabel('greedy_max_probability')).toBe('GMP')
  })

  it('frontier_coverage → FC', () => {
    expect(strategyLabel('frontier_coverage')).toBe('FC')
  })

  it('single word → its first letter uppercased', () => {
    expect(strategyLabel('greedy')).toBe('G')
  })
})

// ---------------------------------------------------------------------------
// drawDetectionRing
// ---------------------------------------------------------------------------

describe('drawDetectionRing', () => {
  it('transparent color → does not draw', () => {
    const ctx = new FakeCtx()
    drawDetectionRing(ctx as unknown as CanvasRenderingContext2D, 10, 10, 5, 'transparent')
    expect(ctx.ops).not.toContain('stroke')
  })

  it('a real color → strokes an arc', () => {
    const ctx = new FakeCtx()
    drawDetectionRing(ctx as unknown as CanvasRenderingContext2D, 10, 10, 5, '#ff0000')
    expect(ctx.ops).toEqual(['beginPath', 'arc', 'stroke'])
    expect(ctx.strokeStyle).toBe('#ff0000')
  })
})

// ---------------------------------------------------------------------------
// drawStrategyLabel
// ---------------------------------------------------------------------------

describe('drawStrategyLabel', () => {
  it('draws the label text at the given position', () => {
    const ctx = new FakeCtx()
    drawStrategyLabel(ctx as unknown as CanvasRenderingContext2D, 12, 8, 'GMP')
    expect(ctx.fillTextArgs).toEqual([['GMP', 12, 8]])
  })
})

// ---------------------------------------------------------------------------
// drawGrid
// ---------------------------------------------------------------------------

describe('drawGrid', () => {
  it('sets strokeStyle and lineWidth', () => {
    const ctx = new FakeCtx()
    drawGrid(ctx as unknown as CanvasRenderingContext2D, 2, 2, 10)
    expect(ctx.strokeStyle).toBe('#dde')
    expect(ctx.lineWidth).toBe(0.5)
  })

  it('strokes (rows+1) horizontal lines and (cols+1) vertical lines', () => {
    const ctx = new FakeCtx()
    drawGrid(ctx as unknown as CanvasRenderingContext2D, 2, 3, 10)
    const strokeCount = ctx.ops.filter((op) => op === 'stroke').length
    expect(strokeCount).toBe(2 + 1 + (3 + 1))
  })
})

// ---------------------------------------------------------------------------
// drawHeatmap
// ---------------------------------------------------------------------------

describe('drawHeatmap', () => {
  it('fills a rect for each cell with positive intensity', () => {
    const ctx = new FakeCtx()
    drawHeatmap(
      ctx as unknown as CanvasRenderingContext2D,
      [
        [0, 1],
        [0.5, 0],
      ],
      10,
    )
    expect(ctx.fillRectArgs.length).toBe(2)
  })

  it('draws nothing for an empty map', () => {
    const ctx = new FakeCtx()
    drawHeatmap(ctx as unknown as CanvasRenderingContext2D, [], 10)
    expect(ctx.fillRectArgs.length).toBe(0)
  })

  it('skips a sparse row without throwing', () => {
    const ctx = new FakeCtx()
    const sparseMap: number[][] = [[0, 1]]
    sparseMap[2] = [0.5, 0] // leaves index 1 as a hole
    expect(() =>
      drawHeatmap(ctx as unknown as CanvasRenderingContext2D, sparseMap, 10),
    ).not.toThrow()
    expect(ctx.fillRectArgs.length).toBe(2)
  })
})

// ---------------------------------------------------------------------------
// drawMothershipMarker
// ---------------------------------------------------------------------------

describe('drawMothershipMarker', () => {
  it('fills a rect inset by 1px within the cell', () => {
    const ctx = new FakeCtx()
    drawMothershipMarker(ctx as unknown as CanvasRenderingContext2D, 20, 30, 10, '#0044cc')
    expect(ctx.fillStyle).toBe('#0044cc')
    expect(ctx.fillRectArgs).toEqual([[21, 31, 8, 8]])
  })
})

// ---------------------------------------------------------------------------
// drawDroneMarker
// ---------------------------------------------------------------------------

describe('drawDroneMarker', () => {
  it('fills a circle at the given center', () => {
    const ctx = new FakeCtx()
    drawDroneMarker(ctx as unknown as CanvasRenderingContext2D, 25, 35, 4, '#4488ff')
    expect(ctx.fillStyle).toBe('#4488ff')
    expect(ctx.ops).toEqual(['beginPath', 'arc', 'fill'])
  })
})

// ---------------------------------------------------------------------------
// drawVesselMarker
// ---------------------------------------------------------------------------

describe('drawVesselMarker', () => {
  it('draws a filled triangle path', () => {
    const ctx = new FakeCtx()
    drawVesselMarker(ctx as unknown as CanvasRenderingContext2D, 25, 30, 5, 10, '#cc0000')
    expect(ctx.fillStyle).toBe('#cc0000')
    expect(ctx.ops).toEqual(['beginPath', 'moveTo', 'lineTo', 'lineTo', 'closePath', 'fill'])
  })
})
