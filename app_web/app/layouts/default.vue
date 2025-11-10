<script setup lang="ts">

</script>

<template>
  <div class="h-svh flex flex-col bg-surface-100 dark:bg-surface-950 transition-colors duration-200">
    <NuxtLoadingIndicator />
    <Toast />
    <BaseHeader class="shrink-0 border-b border-primary-200 dark:border-primary-900 bg-white dark:bg-surface-900 shadow-sm" />
    <div class="flex-1 overflow-hidden">
      <div class="container mx-auto p-3 md:p-6 h-full">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
