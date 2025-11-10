import type { Role, RoleEdit } from '~/interfaces/accounts'

export const useRolesStore = defineStore('roles', () => {
  const roleApi = useRoleApi()

  const roles = ref<Role[]>([])
  const currentRole = ref<Role | undefined>(undefined)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchRoles() {
    loading.value = true
    error.value = null
    try {
      const data = await roleApi.fetchRoles()
      roles.value = data
      return data
    }
    catch (err) {
      error.value = 'Failed to fetch roles'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function fetchRole(id: string) {
    loading.value = true
    error.value = null
    try {
      const data = await roleApi.fetchRole(id)
      currentRole.value = data
      return data
    }
    catch (err) {
      error.value = 'Failed to fetch role'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function createRole(role: RoleEdit) {
    loading.value = true
    error.value = null
    try {
      const newRole = await roleApi.createRole(role)
      roles.value.push(newRole)
      return newRole
    }
    catch (err) {
      error.value = 'Failed to create role'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function updateRole(id: string, role: RoleEdit) {
    loading.value = true
    error.value = null
    try {
      const updatedRole = await roleApi.updateRole(id, role)
      const index = roles.value.findIndex(r => r.id === id)
      if (index !== -1) {
        roles.value[index] = updatedRole
      }
      if (currentRole.value?.id === id) {
        currentRole.value = updatedRole
      }
      return updatedRole
    }
    catch (err) {
      error.value = 'Failed to update role'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function deleteRole(id: string) {
    loading.value = true
    error.value = null
    try {
      await roleApi.deleteRole(id)
      roles.value = roles.value.filter(r => r.id !== id)
      if (currentRole.value?.id === id) {
        currentRole.value = undefined
      }
    }
    catch (err) {
      error.value = 'Failed to delete role'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrentRole() {
    currentRole.value = undefined
  }

  return {
    roles,
    currentRole,
    loading,
    error,
    fetchRoles,
    fetchRole,
    createRole,
    updateRole,
    deleteRole,
    clearError,
    clearCurrentRole,
  }
})
