<template>
  <div class="game-canvas-wrapper">
    <canvas ref="canvasRef" :width="CANVAS_W" :height="CANVAS_H" class="game-canvas" />
    <p v-if="!store.gameState" class="status">{{ store.status }}</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'

import { cellToPixelX, cellToPixelY, drawCone } from './canvas-helpers'
import { useGameStore } from '@/stores/game'

const CELL_SIZE = 10
const GRID_ROWS = 50
const GRID_COLS = 50
const CANVAS_W = GRID_COLS * CELL_SIZE
const CANVAS_H = GRID_ROWS * CELL_SIZE
const CONE_HALF_ANGLE = 60
const CONE_RANGE_PX = 8 * CELL_SIZE

const canvasRef = ref<HTMLCanvasElement | null>(null)
const store = useGameStore()
const flashingDrones = ref(new Set<number>())

function drawGrid(ctx: CanvasRenderingContext2D): void {
  ctx.strokeStyle = '#dde'
  ctx.lineWidth = 0.5
  for (let r = 0; r <= GRID_ROWS; r++) {
    ctx.beginPath()
    ctx.moveTo(0, r * CELL_SIZE)
    ctx.lineTo(CANVAS_W, r * CELL_SIZE)
    ctx.stroke()
  }
  for (let c = 0; c <= GRID_COLS; c++) {
    ctx.beginPath()
    ctx.moveTo(c * CELL_SIZE, 0)
    ctx.lineTo(c * CELL_SIZE, CANVAS_H)
    ctx.stroke()
  }
}

function render(): void {
  const canvas = canvasRef.value
  if (!canvas || !store.gameState) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const { mothership, drones, vessel, detection_events } = store.gameState
  const half = CELL_SIZE / 2

  flashingDrones.value = new Set(detection_events.map((e) => e.drone_idx))

  ctx.clearRect(0, 0, CANVAS_W, CANVAS_H)
  drawGrid(ctx)

  // Cones — rendered behind entities
  for (let i = 0; i < drones.length; i++) {
    const drone = drones[i]
    if (!drone) continue
    const color = flashingDrones.value.has(i) ? 'rgba(255, 140, 0, 0.4)' : 'rgba(0, 68, 204, 0.15)'
    drawCone(
      ctx,
      cellToPixelX(drone.col, CELL_SIZE) + half,
      cellToPixelY(drone.row, CELL_SIZE) + half,
      drone.heading[0],
      drone.heading[1],
      CONE_HALF_ANGLE,
      CONE_RANGE_PX,
      color,
    )
  }

  // BlueMothership — filled square (dark blue)
  ctx.fillStyle = '#0044cc'
  ctx.fillRect(
    cellToPixelX(mothership.col, CELL_SIZE) + 1,
    cellToPixelY(mothership.row, CELL_SIZE) + 1,
    CELL_SIZE - 2,
    CELL_SIZE - 2,
  )

  // BlueDrone — circle (light blue)
  ctx.fillStyle = '#4488ff'
  for (const drone of drones) {
    ctx.beginPath()
    ctx.arc(
      cellToPixelX(drone.col, CELL_SIZE) + half,
      cellToPixelY(drone.row, CELL_SIZE) + half,
      half - 1,
      0,
      2 * Math.PI,
    )
    ctx.fill()
  }

  // RedVessel — triangle (red)
  ctx.fillStyle = '#cc0000'
  const vx = cellToPixelX(vessel.col, CELL_SIZE) + half
  const vy = cellToPixelY(vessel.row, CELL_SIZE)
  ctx.beginPath()
  ctx.moveTo(vx, vy + 1)
  ctx.lineTo(vx - half + 1, vy + CELL_SIZE - 1)
  ctx.lineTo(vx + half - 1, vy + CELL_SIZE - 1)
  ctx.closePath()
  ctx.fill()
}

onMounted(() => store.connect())
onUnmounted(() => store.disconnect())
watch(() => store.gameState, render, { deep: true })
</script>
