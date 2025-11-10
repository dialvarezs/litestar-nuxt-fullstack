import type { Permission, PermissionEdit } from '~/interfaces/accounts'

export function usePermissionApi() {
  const { $api } = useNuxtApp()
  const baseUrl = '/proxy/accounts/permissions'

  return {
    fetchPermissions: () => $api<Permission[]>(baseUrl),
    fetchPermission: (id: string) => $api<Permission>(`${baseUrl}/${id}`),
    createPermission: (permission: PermissionEdit) => $api<Permission>(baseUrl, {
      method: 'POST',
      body: permission,
    }),
    updatePermission: (id: string, permission: Partial<PermissionEdit>) => $api<Permission>(`${baseUrl}/${id}`, {
      method: 'PATCH',
      body: permission,
    }),
    deletePermission: (id: string) => $api(`${baseUrl}/${id}`, {
      method: 'DELETE',
    }),
  }
}
