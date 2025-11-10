export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const config = useRuntimeConfig()

  try {
    await $fetch<any>('/accounts/auth/login', {
      baseURL: (config.public.apiBaseUrl as string) || 'http://localhost:8000',
      method: 'POST',
      body: new URLSearchParams({
        username: body.username,
        password: body.password,
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      // Capture response headers to extract cookies
      onResponse: ({ response }) => {
        // Copy token cookie from backend to our frontend
        const setCookieHeaders = response.headers.get('set-cookie')
        if (setCookieHeaders) {
          const tokenMatch = setCookieHeaders.match(/token=([^;]+)/)
          if (tokenMatch && tokenMatch[1]) {
            // Remove quotes if present - URL decode the token value
            const token = decodeURIComponent(tokenMatch[1]).replace(/^"(.*)"$/, '$1')
            setCookie(event, 'auth-token', token, {
              httpOnly: true,
              secure: !config.public.dev,
              sameSite: 'strict',
              maxAge: 60 * 60 * 24,
              path: '/',
            })
          }
        }
      },
    })

    const authToken = getCookie(event, 'auth-token')
    if (authToken) {
      try {
        const user = await $fetch('/accounts/users/me', {
          baseURL: (config.public.apiBaseUrl as string) || 'http://localhost:8000',
          headers: {
            Authorization: authToken,
          },
        })

        return {
          user,
          message: 'Login successful',
        }
      }
      catch (userError) {
        console.error('Failed to fetch user data:', userError)
      }
    }

    return {
      user: null,
      message: 'Login successful',
    }
  }
  catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 401,
      statusMessage: error.data?.detail || 'Authentication failed',
    })
  }
})
