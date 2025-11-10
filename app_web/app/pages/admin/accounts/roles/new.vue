<script setup lang="ts">
import type { RoleEdit } from '~/interfaces/accounts'

const rolesStore = useRolesStore()
const { showError, showSuccess } = useToastsWithDefaults()

async function onCancel() {
  await navigateTo('/admin/accounts/roles')
}

async function submitRole(data: RoleEdit) {
  try {
    await rolesStore.createRole(data)
    showSuccess('Rol creado correctamente')
    await navigateTo('/admin/accounts/roles')
  }
  catch (errorObj: any) {
    const detail = errorObj?.data?.detail || errorObj?.message || 'Ocurrió un error al crear el rol'
    showError('Error al crear rol', detail)
  }
}
</script>

<template>
  <AdminRoleForm @save="submitRole" @cancel="onCancel" />
</template>
