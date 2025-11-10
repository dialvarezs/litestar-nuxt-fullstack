<script setup lang="ts">
definePageMeta({
  layout: false,
})

const authStore = useAuthStore()
const route = useRoute()

onMounted(async () => {
  try {
    await authStore.fetchCurrentUser()

    const redirectTo = route.query.redirect as string || '/'
    await navigateTo(redirectTo)
  }
  catch {
    const redirectParam = route.query.redirect as string
    await navigateTo(`/auth/login?redirect=${encodeURIComponent(redirectParam || '/')}`)
  }
})
</script>

<template>
  <div class="min-h-screen relative bg-surface-100 dark:bg-surface-950 transition-colors duration-200">
    <div style="position: absolute; top: 1.5rem; right: 1.5rem; z-index: 10;">
      <ThemeToggler />
    </div>

    <div class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <div class="mb-8">
          <div class="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Icon name="mdi:flask" class="text-white" size="32" />
          </div>
          <h1 class="text-3xl font-bold text-surface-700 dark:text-surface-300">
            App
          </h1>
        </div>

        <div class="mb-6">
          <ProgressSpinner style-class="w-12 h-12" stroke-width="4" />
        </div>

        <p class="text-surface-600 dark:text-surface-400 text-lg">
          Cargando...
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
