<script setup lang="ts">
import type { User } from '~/interfaces/accounts'

const usersStore = useUsersStore()

await useAsyncData('users', async () => {
  await usersStore.fetchUsers()
  return true
})

const users = computed(() => usersStore.users)

const fields = [
  { key: 'username', label: 'Usuario' },
  { key: 'email', label: 'Email' },
  { key: 'fullname', label: 'Nombre' },
  { key: 'isActive', label: 'Activo' },
  { key: 'lastLogin', label: 'Último acceso', formatter: formatDatetime },
]

async function onCreate() {
  await navigateTo({ path: `users/new` })
}

async function onEdit(user: User) {
  await navigateTo({ path: `users/${user.id}/edit` })
}
</script>

<template>
  <AdminTable
    :items="users" :fields="fields"
    @create="onCreate" @edit="onEdit"
  >
    <template #custom-columns>
      <Column key="roles" header="Roles">
        <template #body="{ data }">
          <Tag v-for="role in data.roles" :key="role.id" severity="secondary" class="mr-1 !py-1">
            {{ role.name }}
          </Tag>
        </template>
      </Column>
    </template>
  </AdminTable>
</template>
