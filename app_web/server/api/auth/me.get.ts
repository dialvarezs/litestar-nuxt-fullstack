export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const authToken = getCookie(event, 'auth-token')

  if (!authToken) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Not authenticated',
    })
  }

  try {
    // Fetch current user from external API
    const user = await $fetch('/accounts/users/me', {
      baseURL: (config.public.apiBaseUrl as string) || 'http://localhost:8000',
      headers: {
        Authorization: authToken, // Token already includes "Bearer " prefix
      },
    })

    return user
  }
  catch (error: any) {
    // If token is invalid, clear cookies
    if (error.statusCode === 401) {
      deleteCookie(event, 'auth-token')
    }

    throw createError({
      statusCode: error.statusCode || 401,
      statusMessage: error.data?.detail || 'Authentication failed',
    })
  }
})
