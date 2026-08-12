export function cellToPixelX(col: number, cellSize: number): number {
  return col * cellSize
}

export function cellToPixelY(row: number, cellSize: number): number {
  return row * cellSize
}

export function heatmapIntensity(value: number, max: number): number {
  if (max <= 0) return 0
  return Math.max(0, Math.min(1, value / max))
}

export function drawHeatmapCell(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  intensity: number,
): void {
  if (intensity <= 0) return
  ctx.fillStyle = `rgba(220, 20, 60, ${intensity * 0.7})`
  ctx.fillRect(x, y, size, size)
}

const DETECTION_STATE_COLORS: Record<string, string> = {
  signaling: '#ffd700',
  confirming: '#ff8c00',
  tracking: '#ff0000',
}

export function detectionStateColor(state: string): string {
  return DETECTION_STATE_COLORS[state] ?? 'transparent'
}

export function strategyLabel(strategy: string): string {
  return strategy
    .split('_')
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
}

export function drawDetectionRing(
  ctx: CanvasRenderingContext2D,
  centerX: number,
  centerY: number,
  radius: number,
  color: string,
): void {
  if (color === 'transparent') return
  ctx.beginPath()
  ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
  ctx.strokeStyle = color
  ctx.lineWidth = 1.5
  ctx.stroke()
}

export function drawStrategyLabel(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  label: string,
): void {
  ctx.fillStyle = '#000'
  ctx.font = '8px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText(label, x, y)
}

export function drawGrid(
  ctx: CanvasRenderingContext2D,
  rows: number,
  cols: number,
  cellSize: number,
): void {
  const width = cols * cellSize
  const height = rows * cellSize
  ctx.strokeStyle = '#dde'
  ctx.lineWidth = 0.5
  for (let r = 0; r <= rows; r++) {
    ctx.beginPath()
    ctx.moveTo(0, r * cellSize)
    ctx.lineTo(width, r * cellSize)
    ctx.stroke()
  }
  for (let c = 0; c <= cols; c++) {
    ctx.beginPath()
    ctx.moveTo(c * cellSize, 0)
    ctx.lineTo(c * cellSize, height)
    ctx.stroke()
  }
}

export function drawHeatmap(
  ctx: CanvasRenderingContext2D,
  map: number[][],
  cellSize: number,
): void {
  let max = 0
  for (const row of map) {
    if (!row) continue
    for (const value of row) {
      if (value > max) max = value
    }
  }
  for (let r = 0; r < map.length; r++) {
    const row = map[r]
    if (!row) continue
    for (let c = 0; c < row.length; c++) {
      const intensity = heatmapIntensity(row[c] ?? 0, max)
      drawHeatmapCell(
        ctx,
        cellToPixelX(c, cellSize),
        cellToPixelY(r, cellSize),
        cellSize,
        intensity,
      )
    }
  }
}

export function drawMothershipMarker(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  cellSize: number,
  color: string,
): void {
  ctx.fillStyle = color
  ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2)
}

export function drawDroneMarker(
  ctx: CanvasRenderingContext2D,
  centerX: number,
  centerY: number,
  radius: number,
  color: string,
): void {
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
  ctx.fill()
}

export function drawVesselMarker(
  ctx: CanvasRenderingContext2D,
  centerX: number,
  topY: number,
  halfSize: number,
  cellSize: number,
  color: string,
): void {
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.moveTo(centerX, topY + 1)
  ctx.lineTo(centerX - halfSize + 1, topY + cellSize - 1)
  ctx.lineTo(centerX + halfSize - 1, topY + cellSize - 1)
  ctx.closePath()
  ctx.fill()
}

export function drawCone(
  ctx: CanvasRenderingContext2D,
  originX: number,
  originY: number,
  headingDrow: number,
  headingDcol: number,
  halfAngleDeg: number,
  rangePx: number,
  color: string,
): void {
  const centerAngle = Math.atan2(headingDrow, headingDcol)
  const halfRad = halfAngleDeg * (Math.PI / 180)
  ctx.beginPath()
  ctx.moveTo(originX, originY)
  ctx.arc(originX, originY, rangePx, centerAngle - halfRad, centerAngle + halfRad)
  ctx.closePath()
  ctx.fillStyle = color
  ctx.fill()
}
