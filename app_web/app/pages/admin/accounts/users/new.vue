<script setup lang="ts">
import type { UserEdit } from '~/interfaces/accounts'

const usersStore = useUsersStore()

const { showError, showSuccess } = useToastsWithDefaults()

async function onCancel() {
  await navigateTo('/admin/accounts/users')
}

async function submitUser(data: UserEdit) {
  try {
    await usersStore.createUser(data)
    showSuccess('Usuario creado correctamente')
    await navigateTo('/admin/accounts/users')
  }
  catch (errorObj: any) {
    const detail = errorObj?.data?.detail || errorObj?.message || 'Ocurrió un error al crear el usuario'
    showError('Error al crear usuario', detail)
  }
}
</script>

<template>
  <AdminUserForm @save="submitUser" @cancel="onCancel" />
</template>

<style scoped>

</style>
