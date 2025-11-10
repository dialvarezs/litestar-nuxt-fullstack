<script setup lang="ts">
import type { FormSubmitEvent } from '@primevue/forms'

import { valibotResolver } from '@primevue/forms/resolvers/valibot'
import * as v from 'valibot'

import type { PasswordUpdate } from '~/interfaces/accounts'

const authStore = useAuthStore()
const toast = useToast()

const initialValues = ref<PasswordUpdate & { confirmPassword: string }>({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const resolver = valibotResolver(
  v.pipe(
    v.object({
      currentPassword: v.pipe(
        v.string(),
        v.nonEmpty('La contraseña actual es requerida'),
      ),
      newPassword: v.pipe(
        v.string(),
        v.minLength(8, 'La nueva contraseña debe tener al menos 8 caracteres'),
      ),
      confirmPassword: v.pipe(
        v.string(),
        v.nonEmpty('Confirma tu nueva contraseña'),
      ),
    }),
    v.forward(
      v.partialCheck(
        [['newPassword'], ['confirmPassword']],
        input => input.newPassword === input.confirmPassword,
        'Las contraseñas no coinciden',
      ),
      ['confirmPassword'],
    ),
  ),
)

async function onFormSubmit({ valid, states }: FormSubmitEvent) {
  if (valid) {
    authStore.clearError()

    const success = await authStore.changePassword({
      currentPassword: states.currentPassword?.value,
      newPassword: states.newPassword?.value,
    })

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Contraseña actualizada',
        detail: 'Tu contraseña ha sido cambiada exitosamente',
        life: 3000,
      })

      navigateTo('/')
    }
  }
}

async function handleCancel() {
  await navigateTo('/')
}
</script>

<template>
  <div class="flex items-center justify-center min-h-full">
    <div class="w-full max-w-md form-container">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <Icon name="mdi:lock" class="text-white" size="32" />
        </div>
        <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-100">
          Cambia tu Contraseña
        </h1>
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
              <Password
                id="currentPassword"
                name="currentPassword"
                :feedback="false"
                toggle-mask
                fluid
                :disabled="authStore.loading"
                autocomplete="current-password"
              />
              <label for="currentPassword">Contraseña actual</label>
            </FloatLabel>
            <Message v-if="$form.currentPassword?.invalid" severity="error" size="small" variant="simple">
              {{ $form.currentPassword.error.message }}
            </Message>
          </div>

          <div class="flex flex-col">
            <FloatLabel variant="on">
              <Password
                id="newPassword"
                name="newPassword"
                :feedback="false"
                toggle-mask
                fluid
                :disabled="authStore.loading"
                autocomplete="new-password"
              />
              <label for="newPassword">Nueva contraseña</label>
            </FloatLabel>
            <Message v-if="$form.newPassword?.invalid" severity="error" size="small" variant="simple">
              {{ $form.newPassword.error.message }}
            </Message>
          </div>

          <div class="flex flex-col">
            <FloatLabel variant="on">
              <Password
                id="confirmPassword"
                name="confirmPassword"
                :feedback="false"
                toggle-mask
                fluid
                :disabled="authStore.loading"
                autocomplete="new-password"
              />
              <label for="confirmPassword">Confirmar nueva contraseña</label>
            </FloatLabel>
            <Message v-if="$form.confirmPassword?.invalid" severity="error" size="small" variant="simple">
              {{ $form.confirmPassword.error.message }}
            </Message>
          </div>

          <div v-if="authStore.error" class="flex flex-col">
            <Message severity="error" :closable="false" class="text-sm">
              {{ authStore.error }}
            </Message>
          </div>

          <div class="flex gap-3">
            <Button
              type="button"
              :disabled="authStore.loading"
              severity="secondary"
              class="flex-1"
              size="large"
              @click="handleCancel"
            >
              <Icon name="material-symbols:undo" />
              Cancelar
            </Button>
            <Button
              type="submit"
              :loading="authStore.loading"
              :disabled="authStore.loading"
              class="flex-1"
              size="large"
            >
              <Icon name="material-symbols:save" />
              <span v-if="!authStore.loading">Cambiar</span>
              <span v-else>Cambiando...</span>
            </Button>
          </div>
        </Form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-container {
  transform: translateY(-2rem);
}
</style>
