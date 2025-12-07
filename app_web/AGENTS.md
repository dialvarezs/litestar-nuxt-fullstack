# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Project Overview

This is a Nuxt 4 + TypeScript frontend application that connects to a backend API. It uses PrimeVue for UI components, Pinia for state management, and Tailwind CSS with PrimeUI for styling.

## Development Commands

```bash
# Install dependencies
pnpm install

# Start development server (accessible on all network interfaces)
pnpm dev

# Type checking
pnpm typecheck

# Linting
pnpm lint           # Check for issues
pnpm lint:fix       # Auto-fix issues

# Build for production
pnpm build

# Preview production build
pnpm preview
```

## Architecture

### API Communication Architecture

The app uses a sophisticated dual-mode API system:

1. **Client-side requests**: Route through `/api` proxy endpoints to avoid CORS issues
2. **Server-side requests**: Connect directly to backend API

**Key files:**
- `app/plugins/api.ts`: Configures `$api` with automatic snake_case/camelCase conversion and 401 handling
- `server/api/proxy/[...path].ts`: Proxies authenticated requests to backend, auto-handles token expiration
- `server/api/auth/login.post.ts`: Handles login, extracts token from backend, sets httpOnly cookie

### Authentication Flow

1. Login credentials posted to `/api/auth/login`
2. Server endpoint forwards to backend, extracts token from Set-Cookie header
3. Token stored in httpOnly cookie `auth-token` (includes "Bearer " prefix)
4. All subsequent requests include token via cookie
5. 401 responses trigger automatic logout and redirect to login

**Key files:**
- `app/stores/auth.ts`: Auth state management, login/logout/password change
- `app/middleware/auth.global.ts`: Global route guard, redirects unauthenticated users to `/loading`
- `app/pages/loading.vue`: Attempts to restore auth, redirects to login or intended page

### State Management Pattern

All stores follow a consistent pattern with Pinia:
- Composable API layer (`useXxxApi`) for backend communication
- Store layer (`useXxxStore`) for state management
- Automatic loading/error state handling
- CRUD operations with optimistic updates

**Example:** `app/stores/roles.ts` + `app/composables/api/accounts/useRoleApi.ts`

### API Composables

Two composable patterns:
1. `useAPI`: Wrapper around `useFetch` that uses `$api` instance (for reactive data fetching)
2. `useXxxApi`: Direct API calls using `$api` (for imperative operations in stores)

### Case Conversion

Automatic bidirectional conversion between frontend (camelCase) and backend (snake_case):
- Request bodies: camelCase → snake_case in `api.ts` plugin
- Response data: snake_case → camelCase in `api.ts` plugin
- Depth limit: 4 levels

### Directory Structure

```
app/
├── assets/styles/     # Global styles
├── components/        # Vue components
│   ├── admin/        # Admin-specific components (Table, Forms)
│   └── base/         # Base components (Header, ThemeToggler)
├── composables/      # Composables
│   └── api/          # API layer composables by domain
├── interfaces/       # TypeScript interfaces
├── layouts/          # Nuxt layouts
├── middleware/       # Route middleware
├── pages/            # File-based routing
│   ├── admin/        # Admin pages (accounts, roles, users)
│   └── auth/         # Auth pages (login, change-password)
├── plugins/          # Nuxt plugins (api.ts for $api setup)
├── stores/           # Pinia stores
└── utils/            # Utility functions

server/
└── api/              # Server API routes
    ├── auth/         # Auth endpoints (login, logout, me)
    └── proxy/        # Proxy to backend API
```

## Configuration

### Environment Variables

Set `NUXT_PUBLIC_API_BASE_URL` to configure backend API URL (defaults to `http://localhost:8000`).

### ESLint

Uses @antfu/eslint-config with perfectionist for import/export sorting. CLAUDE.md is auto-ignored in `eslint.config.mjs`.

### Theme

PrimeVue with Aura preset, dark mode via `.app-dark` class selector. Theme toggle component manages preference in localStorage.

## Module Configuration

- **SSR**: Enabled
- **Auto-imports**: Stores directory auto-imported
- **PrimeVue**: Auto-import enabled, Chart and Editor excluded
- **Icons**: Material Design Icons (mdi) in server bundle
- **Tailwind**: Integrated with tailwindcss-primeui plugin
