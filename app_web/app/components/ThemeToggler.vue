<script setup lang="ts">
const { theme } = storeToRefs(usePreferencesStore())

interface ThemeState {
  name: string
  icon: string
}

const themeStates: ThemeState[] = [
  { name: 'system', icon: 'material-symbols:brightness-4' },
  { name: 'light', icon: 'material-symbols:sunny' },
  { name: 'dark', icon: 'material-symbols:moon-stars' },
] as const

const icon = computed(() => {
  const foundState = themeStates.find(state => state.name === theme.value)
  return foundState?.icon ?? themeStates[0]!.icon
})

let mediaQuery: MediaQueryList | null = null

function handleSystemThemeChange(_e: MediaQueryListEvent) {
  if (theme.value === 'system') {
    applyTheme()
  }
}

function applyTheme() {
  let themeToApply = theme.value
  if (theme.value === 'system') {
    if (!mediaQuery) {
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    }
    themeToApply = mediaQuery.matches ? 'dark' : 'light'
  }

  if (themeToApply === 'dark') {
    document.documentElement.classList.add('app-dark')
  }
  else {
    document.documentElement.classList.remove('app-dark')
  }
}

function toggleTheme() {
  const currentIndex = themeStates.findIndex(state => state.name === theme.value)
  const nextIndex = (currentIndex + 1) % themeStates.length
  const nextTheme = themeStates[nextIndex]

  if (nextTheme) {
    theme.value = nextTheme.name
    applyTheme()
  }
}

onBeforeMount(() => {
  mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', handleSystemThemeChange)
})

onUnmounted(() => {
  if (mediaQuery) {
    mediaQuery.removeEventListener('change', handleSystemThemeChange)
  }
})
</script>

<template>
  <Button
    outlined
    severity="secondary"
    class="p-2 rounded-lg border-surface-300 dark:border-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-all duration-200 hover:border-primary-500 dark:hover:border-primary-400 hover:scale-105"
    @click="toggleTheme()"
  >
    <Icon :name="icon" size="18" class="transition-all duration-200 hover:scale-110 text-surface-600 dark:text-surface-400" />
  </Button>
</template>
