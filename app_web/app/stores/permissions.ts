import type { Permission, PermissionEdit } from '~/interfaces/accounts'

export const usePermissionsStore = defineStore('permissions', () => {
  const permissionApi = usePermissionApi()

  const permissions = ref<Permission[]>([])
  const currentPermission = ref<Permission | undefined>(undefined)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPermissions() {
    loading.value = true
    error.value = null
    try {
      const data = await permissionApi.fetchPermissions()
      permissions.value = data
      return data
    }
    catch (err) {
      error.value = 'Failed to fetch permissions'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function fetchPermission(id: string) {
    loading.value = true
    error.value = null
    try {
      const data = await permissionApi.fetchPermission(id)
      currentPermission.value = data
      return data
    }
    catch (err) {
      error.value = 'Failed to fetch permission'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function createPermission(permission: PermissionEdit) {
    loading.value = true
    error.value = null
    try {
      const newPermission = await permissionApi.createPermission(permission)
      permissions.value.push(newPermission)
      return newPermission
    }
    catch (err) {
      error.value = 'Failed to create permission'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function updatePermission(id: string, permission: Partial<PermissionEdit>) {
    loading.value = true
    error.value = null
    try {
      const updatedPermission = await permissionApi.updatePermission(id, permission)
      const index = permissions.value.findIndex(p => p.id === id)
      if (index !== -1) {
        permissions.value[index] = updatedPermission
      }
      if (currentPermission.value?.id === id) {
        currentPermission.value = updatedPermission
      }
      return updatedPermission
    }
    catch (err) {
      error.value = 'Failed to update permission'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function deletePermission(id: string) {
    loading.value = true
    error.value = null
    try {
      await permissionApi.deletePermission(id)
      permissions.value = permissions.value.filter(p => p.id !== id)
      if (currentPermission.value?.id === id) {
        currentPermission.value = undefined
      }
    }
    catch (err) {
      error.value = 'Failed to delete permission'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrentPermission() {
    currentPermission.value = undefined
  }

  // Computed property to group permissions by resource
  const permissionsByResource = computed(() => {
    const grouped: Record<string, Permission[]> = {}
    permissions.value.forEach((permission) => {
      if (!grouped[permission.resource]) {
        grouped[permission.resource] = []
      }
      grouped[permission.resource]!.push(permission)
    })
    // Sort permissions within each resource by action
    Object.keys(grouped).forEach((resource) => {
      grouped[resource]?.sort((a, b) => a.action.localeCompare(b.action))
    })
    return grouped
  })

  return {
    permissions,
    currentPermission,
    loading,
    error,
    permissionsByResource,
    fetchPermissions,
    fetchPermission,
    createPermission,
    updatePermission,
    deletePermission,
    clearError,
    clearCurrentPermission,
  }
})
