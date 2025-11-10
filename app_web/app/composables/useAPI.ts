import type { UseFetchOptions } from 'nuxt/app'

export const useAPI: typeof useFetch = function useAPI<T>(
  url: string | (() => string),
  options?: UseFetchOptions<T>,
) {
  return useFetch(url, {
    ...options,
    $fetch: useNuxtApp().$api as typeof $fetch,
  })
}
