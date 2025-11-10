<script setup lang="ts">
import type { FormSubmitEvent } from '@primevue/forms'

import { valibotResolver } from '@primevue/forms/resolvers/valibot'
import * as v from 'valibot'

import type { LoginCredentials } from '~/interfaces/accounts'

definePageMeta({
  layout: false,
})

const authStore = useAuthStore()
const toast = useToast()
const route = useRoute()

const initialValues = ref<LoginCredentials>({
  username: '',
  password: '',
})

const resolver = valibotResolver(
  v.object({
    username: v.pipe(
      v.string(),
      v.nonEmpty('El nombre de usuario es requerido'),
    ),
    password: v.pipe(
      v.string(),
      v.nonEmpty('La contraseña es requerida'),
    ),
  }),
)

function onFormSubmit({ valid, states }: FormSubmitEvent) {
  if (valid) {
    authStore.clearError()

    // Get redirect parameter from URL directly as fallback
    const redirectTo = route.query.redirect as string
      || (typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('redirect') : null) || undefined

    authStore.login({
      username: states.username?.value,
      password: states.password?.value,
    }, redirectTo)
  }
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    const redirectTo = route.query.redirect as string
      || (typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('redirect') : null) || '/'
    await navigateTo(redirectTo)
  }

  if (import.meta.client && sessionStorage.getItem('tokenExpiredMessage')) {
    toast.add({
      severity: 'warn',
      summary: 'Sesión expirada',
      detail: 'Tu token de acceso ha expirado. Por favor, inicia sesión nuevamente.',
      life: 5000,
    })
    sessionStorage.removeItem('tokenExpiredMessage')
  }
})
</script>

<template>
  <div class="min-h-screen bg-surface-100 dark:bg-surface-950 px-4 flex items-center justify-center">
    <NuxtLoadingIndicator />
    <Toast />
    <div class="fixed top-6 right-6">
      <ThemeToggler />
    </div>

    <div class="w-full max-w-md form-container">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <Icon name="mdi:flask" class="text-white" size="32" />
        </div>
        <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-100">
          App
        </h1>
        <p class="text-surface-600 dark:text-surface-400 mt-2">
          Inicia sesión en tu cuenta
        </p>
      </div>

      <div class="bg-white dark:bg-surface-900 rounded-2xl shadow-lg border border-surface-200 dark:border-surface-700 p-8">
        <Form
          v-slot="$form"
          :initial-values="initialValues"
          :resolver="resolver"
          class="flex flex-col gap-6"
          @submit="onFormSubmit"
        >
          <div class="flex flex-col">
            <FloatLabel variant="on">
              <InputText
                id="username"
                name="username"
                type="text"
                fluid
                :disabled="authStore.loading"
                autocomplete="username"
              />
              <label for="username">Nombre de usuario</label>
            </FloatLabel>
            <Message v-if="$form.username?.invalid" severity="error" size="small" variant="simple">
              {{ $form.username.error.message }}
            </Message>
          </div>

          <div class="flex flex-col">
            <FloatLabel variant="on">
              <Password
                id="password"
                name="password"
                :feedback="false"
                toggle-mask
                fluid
                :disabled="authStore.loading"
                autocomplete="current-password"
              />
              <label for="password">Contraseña</label>
            </FloatLabel>
            <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">
              {{ $form.password.error.message }}
            </Message>
          </div>

          <div v-if="authStore.error" class="flex flex-col">
            <Message severity="error" :closable="false" class="text-sm">
              {{ authStore.error }}
            </Message>
          </div>

          <Button
            type="submit"
            :loading="authStore.loading"
            :disabled="authStore.loading"
            class="w-full"
            size="large"
          >
            <span v-if="!authStore.loading">Iniciar sesión</span>
            <span v-else>Iniciando sesión...</span>
          </Button>
        </Form>
      </div>

      <div class="text-center mt-8 text-sm text-surface-500 dark:text-surface-400">
        <p>© 2025 App. Todos los derechos reservados.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-container {
  transform: translateY(-2rem);
}
</style>
