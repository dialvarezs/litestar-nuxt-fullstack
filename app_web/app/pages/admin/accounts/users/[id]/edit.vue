<script setup lang="ts">
import type { UserEdit } from '~/interfaces/accounts'

const usersStore = useUsersStore()

const route = useRoute()
const userId = route.params.id as string
const { showError, showSuccess } = useToastsWithDefaults()

await useAsyncData(`user-${userId}`, async () => {
  await usersStore.fetchUser(userId)
  return true
})

const user = computed(() => usersStore.currentUser)

async function onCancel() {
  await navigateTo('/admin/accounts/users')
}

async function submitUser(data: UserEdit) {
  try {
    await usersStore.updateUser(userId, data)
    showSuccess('Usuario actualizado correctamente')
    await navigateTo('/admin/accounts/users')
  }
  catch (errorObj: any) {
    const detail = errorObj?.data?.detail || errorObj?.message || 'Ocurrió un error al actualizar el usuario'
    showError('Error al actualizar usuario', detail)
  }
}
</script>

<template>
  <AdminUserForm :prop-initial-values="user" protect-password @cancel="onCancel" @save="submitUser" />
</template>

<style scoped>

</style>
