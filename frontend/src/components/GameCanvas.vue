<template>
  <div class="game-canvas-wrapper">
    <canvas ref="canvasRef" :width="CANVAS_W" :height="CANVAS_H" class="game-canvas" />
    <p v-if="!store.gameState" class="status">{{ store.status }}</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'

import {
  cellToPixelX,
  cellToPixelY,
  detectionStateColor,
  drawCone,
  drawDetectionRing,
  drawDroneMarker,
  drawGrid,
  drawHeatmap,
  drawMothershipMarker,
  drawStrategyLabel,
  drawVesselMarker,
  strategyLabel,
} from './canvas-helpers'
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

function render(): void {
  const canvas = canvasRef.value
  if (!canvas || !store.gameState) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const { mothership, drones, vessel, detection_events, probability_map } = store.gameState
  const half = CELL_SIZE / 2

  flashingDrones.value = new Set(detection_events.map((e) => e.drone_idx))

  ctx.clearRect(0, 0, CANVAS_W, CANVAS_H)
  drawHeatmap(ctx, probability_map, CELL_SIZE)
  drawGrid(ctx, GRID_ROWS, GRID_COLS, CELL_SIZE)

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
  drawMothershipMarker(
    ctx,
    cellToPixelX(mothership.col, CELL_SIZE),
    cellToPixelY(mothership.row, CELL_SIZE),
    CELL_SIZE,
    '#0044cc',
  )

  // BlueDrone — circle (light blue), detection-state ring, strategy label
  for (const drone of drones) {
    const cx = cellToPixelX(drone.col, CELL_SIZE) + half
    const cy = cellToPixelY(drone.row, CELL_SIZE) + half

    drawDroneMarker(ctx, cx, cy, half - 1, '#4488ff')
    drawDetectionRing(ctx, cx, cy, half + 1, detectionStateColor(drone.detection_state))
    drawStrategyLabel(ctx, cx, cy - half - 2, strategyLabel(drone.strategy))
  }

  // RedVessel — triangle (red)
  drawVesselMarker(
    ctx,
    cellToPixelX(vessel.col, CELL_SIZE) + half,
    cellToPixelY(vessel.row, CELL_SIZE),
    half,
    CELL_SIZE,
    '#cc0000',
  )
}

onMounted(() => store.connect())
onUnmounted(() => store.disconnect())
watch(() => store.gameState, render, { deep: true })
</script>
