# Nuxt 4 Frontend

Modern frontend application built with Nuxt 4, TypeScript, PrimeVue, and Tailwind CSS.

## Requirements
- [bun](https://bun.sh/)

## Quick Start

```bash
bun install              # Install dependencies
cp .env{.example,}       # Copy environment config (edit if necessary)
bun run dev              # Run development server
```

## Development Commands

```bash
# Code quality
bun run typecheck  # Type checking with Vue TypeScript
bun run lint       # Lint with ESLint
bun run lint:fix   # Auto-fix linting issues

# Build and preview
bun run build      # Production build
bun run preview    # Preview production build
```

## Architecture

### Structure
- **nuxt.config.ts** - Nuxt configuration and module setup
- **app/plugins/api.ts** - API client configuration with automatic case conversion
- **app/stores/** - Pinia state management stores
- **app/composables/api/** - API layer composables by domain
- **app/components/** - Vue components (admin/, base/)
- **app/pages/** - File-based routing (admin/, auth/)
- **server/api/** - Server endpoints (auth/, proxy/)

### API Communication
Dual-mode API system for seamless client/server requests:
- **Client-side**: Routes through `/api` proxy endpoints (to avoids CORS)
- **Server-side**: Direct connection to backend API
- Automatic snake_case/camelCase conversion in both directions

### Authentication
- HttpOnly cookie-based auth with JWT tokens
- Token stored in `auth-token` cookie
- Login flow: `/api/auth/login` → backend → token extraction → cookie storage
- Automatic 401 handling with logout and redirect
- Global middleware protection for authenticated views

### State Management
- **Composable API layer** (`useXxxApi`) for backend communication
- **Store layer** (`useXxxStore`) for state management
- Automatic loading/error state handling
- CRUD operations with optimistic updates

## Configuration

Edit `.env` or set environment variables:
- `NUXT_PUBLIC_API_BASE_URL` - Backend API URL (default: `http://localhost:8000`)

**Theme:** PrimeVue with Aura preset and dark mode support. Theme preference stored in localStorage.
