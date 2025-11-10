<script setup lang="ts">
import type { FormSubmitEvent } from '@primevue/forms'

import { valibotResolver } from '@primevue/forms/resolvers/valibot'
import * as v from 'valibot'

import type { Role, RoleEdit } from '~/interfaces/accounts'

interface Props {
  propInitialValues?: Role
}

const {
  propInitialValues = {} as Role,
}: Props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'save', data: RoleEdit): void
  (e: 'cancel'): void
}>()

const initialValues: Ref<RoleEdit> = ref({
  name: propInitialValues.name || '',
  description: propInitialValues.description || '',
  isActive: propInitialValues?.isActive || undefined,
})
const isEdited = computed(() => !!propInitialValues.id)

// Initialize selected permissions from propInitialValues
const selectedPermissionIds = ref<string[]>(
  propInitialValues.permissions?.map(p => p.id) || [],
)

const resolver = valibotResolver(
  v.object({
    name: v.pipe(
      v.string(),
      v.nonEmpty('El nombre del rol es requerido'),
      v.maxLength(50, 'El nombre del rol no puede tener más de 50 caracteres'),
    ),
    description: v.pipe(
      v.string(),
      v.maxLength(255, 'La descripción no puede tener más de 255 caracteres'),
    ),
    isActive: v.boolean(),
  }),
)

function onFormSubmit({ valid, states }: FormSubmitEvent) {
  if (valid) {
    const roleData: RoleEdit = {
      name: states.name?.value,
      description: states.description?.value,
      isActive: states.isActive?.value,
      permissions: selectedPermissionIds.value.map(id => ({ id })),
    }
    emit('save', roleData)
  }
}
</script>

<template>
  <Form
    v-slot="$form" :initial-values="initialValues" :resolver="resolver"
    class="admin-form pb-6"
    @submit="onFormSubmit"
  >
    <h1 class="text-2xl font-bold text-surface-800 dark:text-surface-100">
      {{ isEdited ? 'Modificar rol' : 'Crear rol' }}
    </h1>
    <div class="flex flex-col">
      <FloatLabel variant="on">
        <InputText id="name" name="name" type="text" fluid />
        <label for="name">Nombre del rol</label>
      </FloatLabel>
      <Message v-if="$form.name?.invalid" severity="error" size="small" variant="simple">
        {{ $form.name.error.message }}
      </Message>
    </div>

    <div class="flex flex-col">
      <FloatLabel variant="on">
        <Textarea id="description" name="description" rows="3" fluid />
        <label for="description">Descripción</label>
      </FloatLabel>
      <Message v-if="$form.description?.invalid" severity="error" size="small" variant="simple">
        {{ $form.description.error.message }}
      </Message>
    </div>

    <div v-if="propInitialValues.id" class="flex gap-2">
      <Checkbox id="isActive" name="isActive" binary />
      <label for="isActive">Activo</label>
      <Message v-if="$form.isActive?.invalid" severity="error" size="small" variant="simple">
        {{ $form.isActive.error.message }}
      </Message>
    </div>

    <!-- Permission Selector -->
    <Divider />
    <AdminRolePermissionSelector v-model="selectedPermissionIds" />

    <div class="admin-form-actions">
      <Button class="admin-form-submit" type="submit">
        <Icon name="material-symbols:save" size="18" />
        Guardar
      </Button>
      <Button
        class="admin-form-cancel"
        severity="secondary"
        outlined
        type="button"
        @click="emit('cancel')"
      >
        <Icon name="material-symbols:undo" size="18" />
        Cancelar
      </Button>
    </div>
  </Form>
</template>
