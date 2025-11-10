<script setup lang="ts">
import type { Permission } from '~/interfaces/accounts'

interface Props {
  modelValue: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const permissionsStore = usePermissionsStore()
const loadError = ref<string | null>(null)

function getErrorMessage(error: unknown) {
  if (typeof error === 'string') {
    return error
  }

  if (error && typeof error === 'object') {
    const dataDetail = (error as any).data?.detail || (error as any).data?.message
    if (dataDetail) {
      return dataDetail as string
    }
    if ('message' in (error as any) && typeof (error as any).message === 'string') {
      return (error as any).message
    }
  }

  return 'No se pudieron cargar los permisos. Intenta nuevamente.'
}

async function loadPermissions(force = false) {
  if (!force && permissionsStore.permissions.length > 0) {
    loadError.value = null
    return
  }

  try {
    loadError.value = null
    await permissionsStore.fetchPermissions()
  }
  catch (error) {
    console.error('Failed to load permissions', error)
    loadError.value = getErrorMessage(error)
  }
}

// Load permissions on mount
onMounted(async () => {
  await loadPermissions()
})

const selectedPermissionIds = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value),
})

const searchQuery = ref('')
const activeResources = ref<string[]>([])

// Filter permissions based on search query
const filteredPermissionsByResource = computed(() => {
  const grouped = permissionsStore.permissionsByResource
  if (!searchQuery.value) {
    return grouped
  }

  const query = searchQuery.value.toLowerCase()
  const filtered: Record<string, Permission[]> = {}

  Object.keys(grouped).forEach((resource) => {
    const resourcePerms = grouped[resource]
    if (!resourcePerms)
      return

    const matchingPermissions = resourcePerms.filter(
      p =>
        p.resource.toLowerCase().includes(query)
        || p.action.toLowerCase().includes(query)
        || p.name.toLowerCase().includes(query)
        || p.description?.toLowerCase().includes(query),
    )
    if (matchingPermissions.length > 0) {
      filtered[resource] = matchingPermissions
    }
  })

  return filtered
})

// Get sorted resource names
const sortedResources = computed(() => {
  return Object.keys(filteredPermissionsByResource.value).sort()
})

// Toggle all permissions for a resource
function toggleResourcePermissions(resource: string, selected: boolean) {
  const resourcePermissions = filteredPermissionsByResource.value[resource]
  if (!resourcePermissions)
    return

  const resourcePermissionIds = resourcePermissions.map(p => p.id)

  if (selected) {
    // Add all permissions from this resource
    const newSelection = new Set([...selectedPermissionIds.value, ...resourcePermissionIds])
    selectedPermissionIds.value = Array.from(newSelection)
  }
  else {
    // Remove all permissions from this resource
    selectedPermissionIds.value = selectedPermissionIds.value.filter(
      id => !resourcePermissionIds.includes(id),
    )
  }
}

// Check if all permissions for a resource are selected
function isResourceFullySelected(resource: string): boolean {
  const resourcePermissions = filteredPermissionsByResource.value[resource]
  if (!resourcePermissions)
    return false
  return resourcePermissions.every(p => selectedPermissionIds.value.includes(p.id))
}

// Check if some (but not all) permissions for a resource are selected
function isResourcePartiallySelected(resource: string): boolean {
  const resourcePermissions = filteredPermissionsByResource.value[resource]
  if (!resourcePermissions)
    return false
  const selectedCount = resourcePermissions.filter(p => selectedPermissionIds.value.includes(p.id)).length
  return selectedCount > 0 && selectedCount < resourcePermissions.length
}

// Count of selected permissions
const selectedCount = computed(() => selectedPermissionIds.value.length)
const totalCount = computed(() => permissionsStore.permissions.length)

// Expand all resources when searching
watch(searchQuery, (newValue) => {
  if (newValue) {
    activeResources.value = sortedResources.value
  }
  else {
    activeResources.value = []
  }
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <div v-if="loadError" class="flex flex-col gap-3">
      <Message severity="error" size="small" variant="filled">
        {{ loadError }}
      </Message>
      <Button
        size="small"
        severity="secondary"
        class="w-fit"
        :loading="permissionsStore.loading"
        @click="loadPermissions(true)"
      >
        <Icon name="material-symbols:refresh" />
        Reintentar
      </Button>
    </div>

    <template v-else>
      <div class="flex flex-col gap-2">
        <label class="font-semibold text-surface-800 dark:text-surface-100">
          Permisos
        </label>
        <div class="text-sm text-surface-600 dark:text-surface-400">
          Selecciona los permisos que tendrá este rol ({{ selectedCount }} de {{ totalCount }} seleccionados)
        </div>
      </div>

      <!-- Search -->
      <div class="flex gap-2">
        <IconField class="w-full">
          <InputIcon>
            <Icon name="material-symbols:search" />
          </InputIcon>
          <InputText
            v-model="searchQuery"
            placeholder="Buscar permisos..."
            fluid
          />
        </IconField>
      </div>

      <!-- Loading state -->
      <div v-if="permissionsStore.loading" class="flex justify-center p-4">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <!-- Permissions accordion -->
      <Accordion
        v-else-if="sortedResources.length > 0"
        v-model:value="activeResources"
        multiple
        class="w-full"
      >
        <AccordionPanel
          v-for="resource in sortedResources"
          :key="resource"
          :value="resource"
        >
          <AccordionHeader>
            <div class="flex items-center justify-between w-full pr-4">
              <div class="flex items-center gap-2">
                <Checkbox
                  :model-value="isResourceFullySelected(resource)"
                  :indeterminate="isResourcePartiallySelected(resource)"
                  binary
                  @update:model-value="(val) => toggleResourcePermissions(resource, val)"
                  @click.stop
                />
                <span class="font-semibold capitalize">{{ resource }}</span>
                <Tag
                  :value="`${filteredPermissionsByResource[resource]?.filter(p => selectedPermissionIds.includes(p.id)).length ?? 0}/${filteredPermissionsByResource[resource]?.length ?? 0}`"
                  severity="secondary"
                  size="small"
                />
              </div>
            </div>
          </AccordionHeader>
          <AccordionContent>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 p-2">
              <div
                v-for="permission in filteredPermissionsByResource[resource]"
                :key="permission.id"
                class="flex items-start gap-2"
              >
                <Checkbox
                  :id="`perm-${permission.id}`"
                  v-model="selectedPermissionIds"
                  :value="permission.id"
                  name="permissions"
                />
                <label :for="`perm-${permission.id}`" class="flex flex-col cursor-pointer flex-1">
                  <span class="text-xs text-surface-500 dark:text-surface-500 font-mono">
                    {{ permission.name }}
                  </span>
                  <span v-if="permission.description" class="text-sm text-surface-600 dark:text-surface-400">
                    {{ permission.description }}
                  </span>
                </label>
              </div>
            </div>
          </AccordionContent>
        </AccordionPanel>
      </Accordion>

      <!-- No results -->
      <div
        v-else-if="searchQuery"
        class="text-center p-4 text-surface-600 dark:text-surface-400"
      >
        No se encontraron permisos que coincidan con "{{ searchQuery }}"
      </div>

      <!-- No permissions available -->
      <div
        v-else
        class="text-center p-4 text-surface-600 dark:text-surface-400"
      >
        No hay permisos disponibles
      </div>
    </template>
  </div>
</template>
