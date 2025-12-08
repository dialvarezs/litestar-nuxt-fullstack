import Aura from '@primeuix/themes/aura'
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  modules: [
    '@primevue/nuxt-module',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxt/icon',
    '@nuxt/eslint',
  ],
  ssr: true,
  imports: {
    dirs: ['stores'],
  },
  devtools: {
    enabled: true,
  },
  app: {
    head: {
      link: [
        { rel: 'stylesheet', href: '/critical.css' },
      ],
      script: [
        { src: '/theme-init.js' },
      ],
    },
  },
  css: ['~/assets/styles/main.css'],
  build: {
    transpile: ['nuxt', 'primevue'],
  },
  compatibilityDate: '2025-07-15',
  nitro: {
    compressPublicAssets: true,
    prerender: {
      crawlLinks: true,
    },
  },
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
  eslint: {
    config: {
      standalone: false,
      stylistic: true,
    },
  },
  icon: {
    serverBundle: {
      collections: ['mdi'],
    },
  },
  primevue: {
    autoImport: true,
    components: {
      exclude: ['Chart', 'Editor'],
    },
    options: {
      theme: {
        preset: Aura,
        options: {
          prefix: 'p',
          darkModeSelector: '.app-dark',
          // cssLayer: true,
        },
      },
      ripple: true,
    },
  },
})
