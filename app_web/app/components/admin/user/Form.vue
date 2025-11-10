<script setup lang="ts">
import type { FormInstance, FormSubmitEvent } from '@primevue/forms'

import { valibotResolver } from '@primevue/forms/resolvers/valibot'
import * as v from 'valibot'

import type { User, UserEdit } from '~/interfaces/accounts'

interface Props {
  propInitialValues?: User
  protectPassword?: boolean
}

const {
  propInitialValues = {} as User,
  protectPassword = false,
}: Props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'save', data: UserEdit): void
  (e: 'cancel'): void
}>()

const usersStore = useUsersStore()
const rolesStore = useRolesStore()

const showPasswordField = ref(!protectPassword)
const formRef = ref<FormInstance>()
const initialValues: Ref<UserEdit> = ref({
  username: propInitialValues.username || '',
  email: propInitialValues.email || '',
  fullname: propInitialValues.fullname || '',
  password: '',
  isActive: propInitialValues?.isActive || undefined,
  roles: propInitialValues.roles?.map(role => role.id) || [],
})
const isEdited = computed(() => !!propInitialValues.id)

await rolesStore.fetchRoles()
const activeRoles = computed(() => rolesStore.roles.filter(role => role.isActive))

const resolver = valibotResolver(
  v.objectAsync({
    username: v.pipeAsync(
      v.string(),
      v.nonEmpty('El nombre de usuario es requerido'),
      v.minLength(5, 'El nombre de usuario debe tener al menos 5 caracteres'),
      v.maxLength(20, 'El nombre de usuario no puede tener más de 20 caracteres'),
      v.checkAsync(async (input: string) => {
        if (isEdited.value && input === propInitialValues.username) {
          return true // Skip validation if username hasn't changed
        }
        return (await usersStore.checkUsernameAvailable(input)).available
      }, 'El nombre de usuario ya está en uso'),
    ),
    email: v.union([
      v.literal(''),
      v.pipe(v.string(), v.email('Email no válido')),
    ]),
    fullname: v.pipe(
      v.string(),
      v.nonEmpty('El nombre completo es requerido'),
      v.maxLength(64, 'El nombre completo no puede tener más de 64 caracteres'),
    ),
    password: v.pipe(
      v.string(),
      v.nonEmpty('La contraseña es requerida'),
      v.minLength(8, 'La contraseña debe tener al menos 8 caracteres'),
      v.regex(/[a-z]/, 'Debe contener minúsculas'),
      v.regex(/[A-Z]/, 'Debe contener mayúsculas'),
      v.regex(/\d/, 'Debe contener números'),
      v.regex(/[^A-Z0-9]/i, 'Debe contener símbolos'),
    ),
    roles: v.union([
      v.pipe(v.array(v.string())),
      v.null(),
    ]),
    isActive: v.boolean(),
  }),
)

function enablePasswordField() {
  showPasswordField.value = true
}

function setRandomPassword() {
  const newPassword = randomPassword()

  initialValues.value.password = newPassword

  if (formRef.value?.states.password) {
    formRef.value.states.password.value = newPassword
  }
}

function onFormSubmit({ valid, states }: FormSubmitEvent) {
  if (valid) {
    emit('save', {
      username: states.username?.value,
      email: states.email?.value.trim() || null,
      fullname: states.fullname?.value,
      password: showPasswordField.value ? states.password?.value : undefined,
      isActive: states?.isActive?.value,
      roles: states.roles?.value.map((id: string) => ({ id })),
    })
  }
}
</script>

<template>
  <Form
    ref="formRef"
    v-slot="$form" :initial-values="initialValues" :resolver="resolver"
    class="admin-form"
    @submit="onFormSubmit"
  >
    <h1 class="text-2xl font-bold text-surface-800 dark:text-surface-100">
      {{ isEdited ? 'Modificar usuario' : 'Crear usuario' }}
    </h1>
    <div class="flex flex-col">
      <FloatLabel variant="on">
        <InputText id="username" name="username" type="text" fluid />
        <label for="username">Nombre de usuario</label>
      </FloatLabel>
      <Message v-if="$form.username?.invalid" severity="error" size="small" variant="simple">
        {{ $form.username.error.message }}
      </Message>
    </div>

    <div class="flex flex-col">
      <FloatLabel variant="on">
        <InputText id="email" name="email" type="text" fluid />
        <label for="email">Correo electrónico</label>
      </FloatLabel>
      <Message v-if="$form.email?.invalid" severity="error" size="small" variant="simple">
        {{ $form.email.error.message }}
      </Message>
    </div>

    <div class="flex flex-col">
      <FloatLabel variant="on">
        <InputText id="fullname" name="fullname" type="text" fluid />
        <label for="fullname">Nombre completo</label>
      </FloatLabel>
      <Message v-if="$form.fullname?.invalid" severity="error" size="small" variant="simple">
        {{ $form.fullname.error.message }}
      </Message>
    </div>

    <div class="flex flex-col">
      <InputGroup v-if="!protectPassword || showPasswordField">
        <FloatLabel variant="on">
          <Password id="password" name="password" toggle-mask fluid :feedback="false" />
          <label for="password">Contraseña</label>
        </FloatLabel>
        <InputGroupAddon>
          <Button v-tooltip.top="'Contraseña aleatoria'" text class="!p-1" @click="setRandomPassword">
            <Icon name="material-symbols:sync-lock" size="20" />
          </Button>
        </InputGroupAddon>
      </InputGroup>
      <Button v-else label="Cambiar contraseña" outlined block @click="enablePasswordField" />
      <Message
        v-if="$form.password?.invalid && (!protectPassword || showPasswordField)" severity="error"
        size="small" variant="simple"
      >
        {{ $form.password.error.message }}
      </Message>
    </div>

    <div class="flex flex-col">
      <MultiSelect
        id="roles" name="roles" display="chip" :options="activeRoles" option-label="name" option-value="id"
        show-clear placeholder="Roles"
        :form-control="{ validateOnValueUpdate: true }"
      />
      <Message v-if="$form.roles?.invalid" severity="error" size="small" variant="simple">
        {{ $form.roles.error.message }}
      </Message>
    </div>

    <div v-if="isEdited" class="flex gap-2">
      <ToggleSwitch id="isActive" name="isActive" binary />
      <label for="isActive">Activo</label>
      <Message v-if="$form.isActive?.invalid" severity="error" size="small" variant="simple">
        {{ $form.isActive.error.message }}
      </Message>
    </div>

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

<style scoped>

</style>
