<template>
  <canvas ref="canvasRef" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
</script>
