export function cellToPixelX(col: number, cellSize: number): number {
  return col * cellSize
}

export function cellToPixelY(row: number, cellSize: number): number {
  return row * cellSize
}
