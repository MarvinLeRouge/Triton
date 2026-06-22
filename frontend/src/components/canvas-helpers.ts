export function cellToPixelX(col: number, cellSize: number): number {
  return col * cellSize
}

export function cellToPixelY(row: number, cellSize: number): number {
  return row * cellSize
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
