import type { LoginCredentials, PasswordUpdate, User } from '~/interfaces/accounts'

export const useAuthStore = defineStore('auth', () => {
  const authApi = useAuthApi()
  const userApi = useUserApi()

  const currentUser = ref<User | null>(null)
  const isAuthenticated = computed(() => currentUser.value !== null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function login(credentials: LoginCredentials, redirectTo?: string) {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)
      currentUser.value = response.user
      await navigateTo(redirectTo || '/')
      return true
    }
    catch (err: any) {
      error.value = err?.data?.detail || 'Login failed'
      return false
    }
    finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = null

    // Mark this as an intentional logout to prevent expired token message
    if (import.meta.client) {
      sessionStorage.setItem('intentionalLogout', 'true')
    }

    try {
      await authApi.logout()
      currentUser.value = null
      await navigateTo('/auth/login')
    }
    catch (err: any) {
      // Even if API logout fails, clear local data
      currentUser.value = null
      await navigateTo('/auth/login')
      error.value = 'Logout failed'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser() {
    try {
      currentUser.value = await authApi.fetchMe()
    }
    catch (err) {
      currentUser.value = null
      throw err
    }
  }

  async function refresh() {
    try {
      await fetchCurrentUser()
    }
    catch {
      currentUser.value = null
    }
  }

  function clearError() {
    error.value = null
  }

  async function changePassword(passwordData: PasswordUpdate) {
    loading.value = true
    error.value = null

    try {
      await userApi.updateMyPassword(passwordData)
      return true
    }
    catch (err: any) {
      error.value = err?.data?.detail || 'Password change failed'
      return false
    }
    finally {
      loading.value = false
    }
  }

  function clearAuth() {
    currentUser.value = null
  }

  return {
    currentUser,
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    changePassword,
    fetchCurrentUser,
    refresh,
    clearError,
    clearAuth,
  }
})
