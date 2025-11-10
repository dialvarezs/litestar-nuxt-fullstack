<script setup lang="ts">
const sidebarVisible = ref(false)

const items = [
  {
    label: 'Cuentas',
    icon: 'pi pi-users',
    items: [
      {
        label: 'Usuarios',
        command: () => {
          navigateTo('/admin/accounts/users')
          sidebarVisible.value = false
        },
      },
      {
        label: 'Roles',
        command: () => {
          navigateTo('/admin/accounts/roles')
          sidebarVisible.value = false
        },
      },
    ],
  },
]

function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
}
</script>

<template>
  <div class="flex flex-col md:flex-row gap-4 md:gap-6 h-full">
    <!-- Desktop Sidebar -->
    <aside class="hidden md:block md:w-64 lg:w-72 h-full flex-shrink-0">
      <Card class="h-full !shadow-md border border-surface-200 dark:border-surface-600 bg-white dark:bg-surface-800 rounded-xl overflow-hidden">
        <template #header>
          <div class="px-6 py-5 border-b border-surface-200 dark:border-surface-600">
            <h3 class="text-lg font-semibold text-surface-800 dark:text-surface-100 flex items-center">
              <Icon name="mdi:cog" class="mr-2 text-primary-600 dark:text-primary-400" size="20" />
              Administración
            </h3>
          </div>
        </template>
        <template #content>
          <div class="p-0 bg-white dark:bg-surface-800">
            <PanelMenu
              :model="items"
              :pt="{
                panel: {
                  class: '!p-0',
                },
              }"
            />
          </div>
        </template>
      </Card>
    </aside>

    <!-- Mobile Sidebar Drawer -->
    <Drawer v-model:visible="sidebarVisible" position="left" class="md:hidden">
      <template #header>
        <h3 class="text-lg font-semibold text-surface-800 dark:text-surface-100 flex items-center">
          <Icon name="mdi:cog" class="mr-2 text-primary-600 dark:text-primary-400" size="20" />
          Administración
        </h3>
      </template>
      <PanelMenu
        :model="items"
        :pt="{
          panel: {
            class: '!p-0',
          },
        }"
      />
    </Drawer>

    <!-- Main Content -->
    <main class="flex-1 h-full overflow-hidden shadow-md rounded-xl">
      <Card
        class="h-full border border-surface-200 dark:border-surface-600 bg-white dark:bg-surface-800 pt-2 md:pt-10"
        :pt="{
          root: { class: 'overflow-auto' },
          body: { class: 'h-full overflow-auto' },
          content: { class: 'h-full pb-6' },
        }"
      >
        <template #content>
          <div class="flex h-full flex-col">
            <div v-if="!sidebarVisible" class="md:hidden px-6 pb-4">
              <Button
                type="button"
                outlined
                severity="secondary"
                class="w-full !h-11 justify-center gap-2 text-sm font-medium"
                aria-label="Abrir menú de administración"
                @click="toggleSidebar"
              >
                <Icon name="mdi:menu" size="18" />
                Menú de entidades
              </Button>
            </div>
            <div class="flex-1">
              <NuxtPage />
            </div>
          </div>
        </template>
      </Card>
    </main>
  </div>
</template>
