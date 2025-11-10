<script setup lang="ts">
import type { RoleEdit } from '~/interfaces/accounts'

const rolesStore = useRolesStore()

const route = useRoute()
const roleId = route.params.id as string
const { showError, showSuccess } = useToastsWithDefaults()

await useAsyncData(`role-${roleId}`, async () => {
  await rolesStore.fetchRole(roleId)
  return true
})

const role = computed(() => rolesStore.currentRole)

async function onCancel() {
  await navigateTo('/admin/accounts/roles')
}

async function submitRole(data: RoleEdit) {
  try {
    await rolesStore.updateRole(roleId, data)
    showSuccess('Rol actualizado correctamente')
    await navigateTo('/admin/accounts/roles')
  }
  catch (errorObj: any) {
    const detail = errorObj?.data?.detail || errorObj?.message || 'Ocurrió un error al actualizar el rol'
    showError('Error al actualizar rol', detail)
  }
}
</script>

<template>
  <AdminRoleForm :prop-initial-values="role" @cancel="onCancel" @save="submitRole" />
</template>
