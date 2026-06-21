import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    hmr: {
      // En Docker derrière Traefik, le navigateur doit se connecter au port
      // de Traefik (80 en local, 443 en prod) plutôt qu'au port Vite (5173).
      // Passer HMR_PORT=80 dans le docker-compose.yml pour activer ce comportement.
      clientPort: Number(process.env.HMR_PORT ?? 5173),
    },
  },
})
