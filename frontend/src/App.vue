<template>
  <main>
    <h1>Triton</h1>
    <p>{{ now }}</p>
    <GameCanvas />
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import GameCanvas from '@/components/GameCanvas.vue'

const now = ref(new Date().toLocaleString())
let timer: ReturnType<typeof setInterval>

onMounted(() => {
  timer = setInterval(() => {
    now.value = new Date().toLocaleString()
  }, 1000)
})

onUnmounted(() => clearInterval(timer))
</script>
