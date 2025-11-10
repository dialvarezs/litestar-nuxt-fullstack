<script setup lang="ts">
const authStore = useAuthStore()
const userMenu = ref()
const mobileMenu = ref(false)

const menuItems = [
  { label: 'Inicio', route: '/' },
  { label: 'Admin', route: '/admin' },
]

const userMenuItems = computed(() => [
  { label: 'Cambiar contraseña', action: 'change-password' },
  { label: 'Cerrar sesión', action: 'logout' },
])

function toggleUserMenu(event: Event) {
  userMenu.value.toggle(event)
}

function toggleMobileMenu() {
  mobileMenu.value = !mobileMenu.value
}

function closeMobileMenu() {
  mobileMenu.value = false
}

async function handleUserMenuAction(action: string) {
  if (action === 'logout') {
    await authStore.logout()
  }
  else if (action === 'change-password') {
    await navigateTo('/auth/change-my-password')
  }
}
</script>

<template>
  <div class="w-full px-4 md:px-6 py-4">
    <div class="flex items-center justify-between">
      <!-- Left side - Logo and Navigation -->
      <div class="flex items-center space-x-4 md:space-x-8">
        <!-- Mobile menu button -->
        <button
          class="md:hidden p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
          @click="toggleMobileMenu"
        >
          <Icon name="mdi:menu" size="24" />
        </button>

        <!-- Logo -->
        <div class="flex items-center">
          <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center mr-2 md:mr-3">
            <Icon name="mdi:flask" class="text-white" size="20" />
          </div>
          <h1 class="text-lg md:text-xl font-bold">
            App
          </h1>
        </div>

        <!-- Desktop Navigation Items -->
        <nav class="hidden md:flex items-center space-x-1">
          <router-link
            v-for="item in menuItems"
            :key="item.label"
            :to="item.route"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:bg-surface-100 dark:hover:bg-surface-700 text-surface-700 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400"
          >
            {{ item.label }}
          </router-link>
        </nav>
      </div>

      <!-- Right side - Theme toggle and User menu -->
      <div class="flex items-center space-x-2 md:space-x-3">
        <ThemeToggler />

        <!-- User Menu - Desktop -->
        <div class="hidden md:block relative">
          <button
            class="flex items-center space-x-2 px-4 py-2 rounded-lg border border-surface-300 dark:border-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-all duration-200 text-surface-700 dark:text-surface-300 hover:border-primary-500 dark:hover:border-primary-400"
            @click="toggleUserMenu"
          >
            <div class="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
              <Icon name="mdi:account" class="text-white text-sm" />
            </div>
            <span class="text-sm font-medium">
              {{ authStore.currentUser?.fullname || authStore.currentUser?.username || 'Usuario' }}
            </span>
            <Icon name="mdi:chevron-down" size="16" />
          </button>

          <Popover ref="userMenu">
            <div class="py-2 w-48">
              <button
                v-for="item in userMenuItems"
                :key="item.label"
                class="w-full px-4 py-2 text-left text-sm text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors duration-200 rounded-lg"
                @click="handleUserMenuAction(item.action)"
              >
                {{ item.label }}
              </button>
            </div>
          </Popover>
        </div>

        <!-- User Menu - Mobile (icon only) -->
        <div class="md:hidden relative">
          <button
            class="flex items-center justify-center w-10 h-10 rounded-lg border border-surface-300 dark:border-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-all duration-200 hover:border-primary-500 dark:hover:border-primary-400"
            @click="toggleUserMenu"
          >
            <div class="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
              <Icon name="mdi:account" class="text-white text-sm" />
            </div>
          </button>

          <Popover ref="userMenu">
            <div class="py-2 w-48">
              <button
                v-for="item in userMenuItems"
                :key="item.label"
                class="w-full px-4 py-2 text-left text-sm text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors duration-200 rounded-lg"
                @click="handleUserMenuAction(item.action)"
              >
                {{ item.label }}
              </button>
            </div>
          </Popover>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation Drawer -->
    <Drawer v-model:visible="mobileMenu" position="left" class="md:hidden">
      <template #header>
        <div class="flex items-center">
          <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center mr-3">
            <Icon name="mdi:flask" class="text-white" size="20" />
          </div>
          <h2 class="text-xl font-bold">
            App
          </h2>
        </div>
      </template>

      <nav class="flex flex-col space-y-2">
        <router-link
          v-for="item in menuItems"
          :key="item.label"
          :to="item.route"
          class="px-4 py-3 rounded-lg text-base font-medium transition-all duration-200 hover:bg-surface-100 dark:hover:bg-surface-700 text-surface-700 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400"
          @click="closeMobileMenu"
        >
          {{ item.label }}
        </router-link>
      </nav>
    </Drawer>
  </div>
</template>

<style scoped>

</style>
