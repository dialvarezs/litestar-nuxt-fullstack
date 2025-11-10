import * as changeKeys from 'change-case/keys'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  // For client-side requests, use internal API routes
  // For server-side requests, use external API directly
  const baseURL = import.meta.server
    ? (config.public.apiBaseUrl as string) ?? 'http://localhost:8000'
    : '/api'

  const api = $fetch.create({
    baseURL,

    onRequest({ options }) {
      if (import.meta.server && baseURL !== '/api') {
        const event = nuxtApp.ssrContext?.event
        if (event) {
          const authToken = getCookie(event, 'auth-token')
          if (authToken) {
            options.headers = new Headers(options.headers)
            options.headers.set('Authorization', authToken)
          }
        }
      }

      // Convert object keys to snake_case and stringify, but skip URLSearchParams
      if (options.body && typeof options.body === 'object' && !(options.body instanceof URLSearchParams)) {
        options.body = JSON.stringify(changeKeys.snakeCase(options.body, 4))
      }
    },

    onResponse({ response }) {
      response._data = changeKeys.camelCase(response._data, 4)
    },

    async onResponseError({ response }) {
      if (response.status === 401) {
        if (import.meta.client) {
          const authStore = useAuthStore()

          // Only show expired message if user was previously authenticated
          // and this is not an intentional logout
          const wasAuthenticated = authStore.isAuthenticated
          const isIntentionalLogout = sessionStorage.getItem('intentionalLogout') === 'true'

          authStore.clearAuth()

          if (wasAuthenticated && !isIntentionalLogout) {
            sessionStorage.setItem('tokenExpiredMessage', 'true')
          }

          // Clear the intentional logout flag
          sessionStorage.removeItem('intentionalLogout')

          await nuxtApp.runWithContext(() => navigateTo('/auth/login'))
        }
      }
    },
  })

  return {
    provide: {
      api,
    },
  }
})
