<script setup lang="ts">
import type { Role } from '~/interfaces/accounts'

const rolesStore = useRolesStore()

await useAsyncData('roles', async () => {
  await rolesStore.fetchRoles()
  return true
})

const roles = computed(() => rolesStore.roles)

const fields = [
  { key: 'name', label: 'Nombre' },
  { key: 'description', label: 'Descripción' },
  { key: 'isActive', label: 'Activo' },
]

async function onCreate() {
  await navigateTo({ path: '/admin/accounts/roles/new' })
}

async function onEdit(role: Role) {
  await navigateTo({ path: `/admin/accounts/roles/${role.id}/edit` })
}
</script>

<template>
  <AdminTable
    :items="roles" :fields="fields" :actions="['edit']"
    @create="onCreate" @edit="onEdit"
  />
</template>
