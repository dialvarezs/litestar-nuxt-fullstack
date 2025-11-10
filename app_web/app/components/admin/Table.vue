<script setup lang="ts" generic="T extends { id: any }">
type ActionType = 'info' | 'edit' | 'delete'

interface Field<T> {
  key: keyof T | string
  label: string
  align?: 'left' | 'right' | 'center'
  formatter?: (value: any, item: T) => string
}

interface Props<T> {
  items: T[] | null
  fields: Field<T>[]
  actions?: ActionType[]
  loading?: boolean
  title?: string
  newButtonLabel?: string
}

const {
  items,
  fields,
  actions = ['info', 'edit'],
  loading,
  title,
  newButtonLabel = 'Nuevo',
} = defineProps<Props<T>>()

const emit = defineEmits<{
  (e: 'edit', row: T): void
  (e: 'view', row: T): void
  (e: 'delete', row: T): void
  (e: 'create'): void
}>()

function formatValue(item: T, field: Field<T>): string {
  const key = field.key as string
  const value = item[key as keyof T]

  if (field.formatter) {
    return field.formatter(value, item)
  }

  if (value === null || value === undefined) {
    return ''
  }

  if (typeof (value as any) === 'boolean') {
    return value ? 'Sí' : 'No'
  }

  if (value instanceof Date) {
    return value.toLocaleDateString('es-ES')
  }

  return String(value)
}

function hasAction(action: ActionType): boolean {
  return actions.includes(action)
}
</script>

<template>
  <div>
    <DataTable
      :value="items"
      :loading="loading"
      data-key="id"
      class="w-full"
    >
      <template #header>
        <div class="flex justify-between items-center py-3 rounded-t-lg">
          <div>
            <h2 v-if="title" class="text-xl font-bold text-surface-800 dark:text-surface-100">
              {{ title }}
            </h2>
          </div>
          <Button
            outlined
            severity="secondary"
            class="flex items-center justify-center gap-2 rounded-lg border-primary-500 !px-4 !py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 dark:border-primary-400 dark:text-primary-300 dark:hover:bg-primary-500/10"
            @click="emit('create')"
          >
            <Icon name="mdi:plus" size="18" />
            {{ newButtonLabel }}
          </Button>
        </div>
      </template>
      <template #empty>
        <div class="text-center">
          <Icon name="mdi:alert-circle-outline" size="24" class="text-surface-500 mb-2" />
          <p class="text-surface-600 dark:text-surface-400">
            No hay datos disponibles
          </p>
        </div>
      </template>
      <Column v-for="field in fields" :key="field.key as string" :header="field.label" :align="field.align">
        <template #body="{ data }">
          {{ formatValue(data, field) }}
        </template>
      </Column>
      <slot name="custom-columns" />
      <Column header="Acciones">
        <template #body="{ data }">
          <div class="flex gap-1">
            <Button
              v-if="hasAction('info')" v-tooltip.top="'Ver'" rounded text class="!p-1"
              @click="emit('view', data)"
            >
              <Icon name="material-symbols:info-outline" size="20px" />
            </Button>
            <Button
              v-if="hasAction('edit')" v-tooltip.top="'Editar'" rounded text class="!p-1"
              @click="emit('edit', data)"
            >
              <Icon name="material-symbols:edit-square-outline" size="20px" />
            </Button>
            <Button
              v-if="hasAction('delete')" v-tooltip.top="'Eliminar'" rounded text class="!p-1" severity="danger"
              @click="emit('delete', data)"
            >
              <Icon name="material-symbols:delete-outline" size="20px" />
            </Button>
          </div>
        </template>
      </Column>
    </DataTable>
  </div>
</template>
