# Full Stack Application Template

A modern full-stack web application template built with [Litestar](https://litestar.dev/) backend and [Nuxt](https://nuxt.com/) frontend.

## What's Included

A complete authentication and authorization system with:

- **User Management**: Full CRUD for users with role assignment
- **Role & Permission System**: Granular resource-level permissions (e.g., `users:create`, `roles:read`)
- **Admin Dashboard**: Pre-built UI for managing users, roles, and permissions

## Quick Start

### Prerequisites
- **Backend**: [uv](https://docs.astral.sh/uv/), [just](https://github.com/casey/just)
- **Frontend**: [bun](https://bun.sh/)
- **Database**: PostgreSQL

### Development Setup

```bash
# Clone the repository
git clone https://github.com/dialvarezs/listestar-nuxt-fullstack
cd listestar-nuxt-fullstack

# Backend setup
cd app_api
uv sync
# Configure config.toml if needed
just db upgrade --no-prompt
just run

# Frontend setup (in new terminal)
cd app_web
bun install
bun run dev
```

The backend API will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`.

## Architecture

### Backend (Python/Litestar)

**Tech Stack:**
- **Framework**: Litestar with async SQLAlchemy and Advanced Alchemy
- **Authentication**: JWT OAuth2 password bearer flow with Argon2 hashing
- **Database**: PostgreSQL with UUIDv7 primary keys and audit fields
- **API**: RESTful endpoints with OpenAPI documentation
- **Testing**: pytest with Docker-based test databases

**Layered Architecture:**
- **Controllers** - HTTP request/response handling and routing
- **Services** - Business logic, validation, and data transformation
- **Repositories** - Data access layer (Advanced Alchemy)
- **Models** - SQLAlchemy ORM models
- **DTOs** - Data Transfer Objects for serialization

**Access Control:**
- Permission-based guards for fine-grained access control
- Role-based permissions with many-to-many relationships
- Superuser role bypasses all permission checks

### Frontend (Nuxt 4/Vue 3)
- **Framework**: Nuxt 4 with SSR and Vue 3 Composition API
- **UI Library**: PrimeVue with Aura theme and TailwindCSS
- **State Management**: Pinia stores with TypeScript
- **Validation**: Valibot schemas with @primevue/forms
- **API Integration**: Custom $fetch wrapper with case conversion

## Project Structure

```
project/
├── app_api/                # Python/Litestar Backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy ORM models
│   │   └── api/            # Feature modules by domain
│   │       └── accounts/   # Users, roles, permissions
│   │           ├── users/
│   │           │   ├── controllers.py
│   │           │   ├── services.py
│   │           │   ├── repositories.py
│   │           │   └── dtos.py
│   │           ├── roles/
│   │           └── auth/
│   ├── tests/              # pytest test suite
│   └── migrations/         # Alembic migrations
└── app_web/                # Nuxt 4/Vue 3 Frontend
    ├── app/
    │   ├── components/     # Vue components
    │   ├── composables/    # API composables
    │   ├── stores/         # Pinia stores
    │   └── pages/          # File-based routing
    └── server/             # Nuxt server API
```

## Development Commands

### Backend (`app_api/`)
```bash
just run          # Start dev server with auto-reload
just format       # Format code with ruff
just lint         # Lint and auto-fix
just test         # Run pytest suite
just ty           # Type check with ty
just db upgrade   # Apply database migrations
```

### Frontend (`app_web/`)
```bash
bun run dev       # Start development server
bun run build     # Build for production
bun run typecheck # TypeScript validation
bun run lint:fix  # Format and lint code
```
