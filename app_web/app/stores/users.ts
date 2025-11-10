import type { User, UserEdit } from '~/interfaces/accounts'

export const useUsersStore = defineStore('users', () => {
  const userApi = useUserApi()

  const users = ref<User[]>([])
  const currentUser = ref<User | undefined>(undefined)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchUsers() {
    loading.value = true
    error.value = null
    try {
      const data = await userApi.fetchUsers()
      users.value = data
      return data
    }
    catch (err) {
      error.value = 'Failed to fetch users'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function fetchUser(id: string) {
    loading.value = true
    error.value = null
    try {
      const data = await userApi.fetchUser(id)
      currentUser.value = data
      return data
    }
    catch (err) {
      error.value = 'Failed to fetch user'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function createUser(user: UserEdit) {
    loading.value = true
    error.value = null
    try {
      const newUser = await userApi.createUser(user)
      users.value.push(newUser)
      return newUser
    }
    catch (err) {
      error.value = 'Failed to create user'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function updateUser(id: string, user: UserEdit) {
    loading.value = true
    error.value = null
    try {
      const updatedUser = await userApi.updateUser(id, user)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      if (currentUser.value?.id === id) {
        currentUser.value = updatedUser
      }
      return updatedUser
    }
    catch (err) {
      error.value = 'Failed to update user'
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function checkUsernameAvailable(username: string) {
    try {
      return await userApi.fetchUsernameAvailable(username)
    }
    catch (err) {
      error.value = 'Failed to check username availability'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrentUser() {
    currentUser.value = undefined
  }

  return {
    users,
    currentUser,
    loading,
    error,
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    checkUsernameAvailable,
    clearError,
    clearCurrentUser,
  }
})
