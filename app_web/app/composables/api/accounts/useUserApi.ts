import type { PasswordUpdate, User, UserEdit, UsernameAvailable } from '~/interfaces/accounts'

export function useUserApi() {
  const { $api } = useNuxtApp()
  const baseUrl = '/proxy/accounts/users'

  return {
    fetchUsers: () => $api<User[]>(baseUrl),
    fetchUser: (id: string) => $api<User>(`${baseUrl}/${id}`),
    createUser: (user: UserEdit) => $api<User>(baseUrl, {
      method: 'POST',
      body: user,
    }),
    updateUser: (id: string, user: UserEdit) => $api<User>(`${baseUrl}/${id}`, {
      method: 'PATCH',
      body: user,
    }),
    updateMyPassword: (passwordUpdate: PasswordUpdate) => $api<void>(`${baseUrl}/me/update-password`, {
      method: 'POST',
      body: passwordUpdate,
    }),
    fetchUsernameAvailable: (username: string) => $api<UsernameAvailable>(`${baseUrl}/username-available/`, {
      query: { username },
    }),
  }
}
