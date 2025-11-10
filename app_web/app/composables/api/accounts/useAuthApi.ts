import type { LoginCredentials, User } from '~/interfaces/accounts'

export function useAuthApi() {
  const { $api } = useNuxtApp()

  return {
    login: (credentials: LoginCredentials) => $api<{ user: User, message: string }>(
      '/auth/login',
      {
        method: 'POST',
        body: credentials,
      },
    ),
    logout: () => $api<{ message: string }>('/auth/logout', {
      method: 'POST',
    }),
    fetchMe: () => $api<User>('/auth/me'),
    refresh: () => $api<{ message: string }>('/auth/refresh', {
      method: 'POST',
    }),
  }
}
