export default defineNuxtRouteMiddleware(async (to) => {
  // Skip auth check for auth pages and loading page
  if (to.path.startsWith('/auth/') || to.path === '/loading') {
    return
  }

  const authStore = useAuthStore()

  // If not authenticated, redirect to loading page
  if (!authStore.isAuthenticated) {
    return navigateTo(`/loading?redirect=${encodeURIComponent(to.fullPath)}`)
  }
})
