type UUID = string

export interface UserBase {
  username: string
  email: string
  fullname: string
}

export interface UserEdit extends UserBase {
  password?: string
  isActive?: boolean
  roles: Role[] | string[]
}

export interface User extends UserBase {
  id: UUID
  isActive: boolean
  lastLogin: string
  roles: Role[]
}

export interface Permission {
  id: UUID
  name: string
  resource: string
  action: string
  description?: string
  isActive: boolean
}

export interface PermissionEdit {
  name: string
  resource: string
  action: string
  description?: string
  isActive?: boolean
}

export interface RoleBase {
  name: string
  description: string
  isActive?: boolean
}

export interface Role extends RoleBase {
  id: UUID
  permissions?: Permission[]
}

export interface RoleEdit extends RoleBase {
  permissions?: Array<{ id: string }>
}

export interface UsernameAvailable {
  username: string
  available: boolean
}

export interface PasswordUpdate {
  currentPassword: string
  newPassword: string
}

export interface LoginCredentials {
  username: string
  password: string
}
