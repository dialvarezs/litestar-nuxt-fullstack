export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const path = getRouterParam(event, 'path')
  const authToken = getCookie(event, 'auth-token')

  if (!authToken) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Authentication required',
    })
  }

  try {
    const method = getMethod(event)
    const query = getQuery(event)
    const body = method !== 'GET' ? await readBody(event) : undefined

    // Forward request to external API with auth token
    return await $fetch(`/${path}` as any, {
      baseURL: (config.public.apiBaseUrl as string) || 'http://localhost:8000',
      method: method as any,
      headers: {
        'Authorization': authToken, // Token already includes "Bearer " prefix
        'Content-Type': 'application/json',
      },
      query,
      body,
    })
  }
  catch (error: any) {
    // Handle token expiration - clear auth cookies on 401
    if (error.statusCode === 401) {
      deleteCookie(event, 'auth-token')
    }

    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.data?.detail || error.statusMessage || 'API request failed',
    })
  }
})
