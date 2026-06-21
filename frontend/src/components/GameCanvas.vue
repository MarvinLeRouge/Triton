<template>
  <div>
    <canvas ref="canvasRef" />
    <p class="status">{{ store.status }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { useGameStore } from '@/stores/game'

const canvasRef = ref<HTMLCanvasElement | null>(null)
const store = useGameStore()
</script>
