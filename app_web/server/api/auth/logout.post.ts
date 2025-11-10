export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const authToken = getCookie(event, 'auth-token')

  try {
    // Attempt to logout from external API if token exists
    if (authToken) {
      await $fetch('/accounts/auth/logout', {
        baseURL: (config.public.apiBaseUrl as string) || 'http://localhost:8000',
        method: 'POST',
        headers: {
          Authorization: authToken, // Token already includes "Bearer " prefix
        },
      })
    }
  }
  catch {
    // Continue with local logout even if API logout fails
  }

  // Clear authentication cookies
  deleteCookie(event, 'auth-token', {
    httpOnly: true,
    secure: !config.public.dev,
    sameSite: 'strict',
    path: '/',
  })

  return {
    message: 'Logged out successfully',
  }
})
