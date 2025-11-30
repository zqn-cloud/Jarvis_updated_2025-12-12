import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // 允许外部访问
    allowedHosts: ['.trycloudflare.com'] // 允许 cloudflare tunnel 域名
  }
})
