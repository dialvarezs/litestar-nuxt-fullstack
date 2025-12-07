# Full Stack Application Template

A modern full-stack web application template built with [Litestar](https://litestar.dev/) backend and [Nuxt](https://nuxt.com/) frontend.

## What's Included

A complete authentication and authorization system with:

- **User Management**: Full CRUD for users with role assignment
- **Role & Permission System**: Granular resource-level permissions
- **Admin Dashboard**: Pre-built UI for managing users, roles, and permissions

## Quick Start

### Prerequisites
- PostgreSQL database
- **Backend**: [uv](https://docs.astral.sh/uv/), [just](https://github.com/casey/just) → See [app_api/README.md](app_api/README.md)
- **Frontend**: [bun](https://bun.sh/) → See [app_web/README.md](app_web/README.md)

### Development Setup

```bash
# Backend setup
cd app_api
uv sync
just db upgrade --no-prompt
just run

# Frontend setup (in new terminal)
cd app_web
bun install
bun run dev
```

The backend API runs at `http://localhost:8000` and the frontend at `http://localhost:3000`.

## Documentation

- **Backend**: See [app_api/README.md](app_api/README.md) for architecture, commands, and configuration
- **Frontend**: See [app_web/README.md](app_web/README.md) for architecture, commands, and configuration

## Deployment

Includes deployment setup using rootless containers with Podman + Quadlet.
See [deploy/README.md](deploy/README.md) for detailed information.
