export const usePreferencesStore = defineStore('preferences', () => {
  const theme = useCookie('theme', {
    default: () => 'system',
    sameSite: 'lax',
    secure: false,
    httpOnly: false,
  })

  return { theme }
})
