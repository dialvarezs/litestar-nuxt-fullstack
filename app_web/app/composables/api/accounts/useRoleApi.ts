import type { Role, RoleEdit } from '~/interfaces/accounts'

export function useRoleApi() {
  const { $api } = useNuxtApp()
  const baseUrl = '/proxy/accounts/roles'

  return {
    fetchRoles: () => $api<Role[]>(baseUrl),
    fetchRole: (id: string) => $api<Role>(`${baseUrl}/${id}`),
    createRole: (role: RoleEdit) => $api<Role>(baseUrl, {
      method: 'POST',
      body: role,
    }),
    updateRole: (id: string, role: RoleEdit) => $api<Role>(`${baseUrl}/${id}`, {
      method: 'PATCH',
      body: role,
    }),
    deleteRole: (id: string) => $api(`${baseUrl}/${id}`, {
      method: 'DELETE',
    }),
  }
}
