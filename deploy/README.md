# Deployment with Podman

- Rootless Podman + Quadlet is used to run the API, frontend, and Postgres in a single pod.
- Default exposed ports are 10101 (API) and 10102 (web).
- Run everything as a non-root user and put a reverse proxy (Caddy/Traefik/NGINX) in front.
- The frontend proxies traffic to the API inside the pod, so only the web port needs to be published for a functional app.

> All paths below assume you run commands from `deploy/` so the hostPath mounts in `app-pod.yaml` resolve correctly.

## Prerequisites

- Podman with Quadlet support (systemd user services enabled).
- `sudo loginctl enable-linger <user>` so the pod can start automatically at boot.
- `sudo systemctl enable tmp.mount` to avoid Podman boot ID errors.

## 1) Build container images

`./build.sh [api|web|all]` (default `all`) builds images tagged `app_api:latest` and `app_web:latest`.

## 2) Secrets

1) Copy and lock down secrets: `cp app-secrets{.example,}.yaml && chmod 600 app-secrets.yaml`
2) Edit `app-secrets.yaml`:
   - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Postgres credentials and database name.
   - `DATABASE_URL`: Full SQLAlchemy URL (e.g., `postgresql+asyncpg://pguser:pgsecret@db:5432/app`).
3) Create the secret: `podman kube play app-secrets.yaml`

## 3) API config + optional DB init

- Copy API config: `cp ../app_api/config.example.toml api-config.toml` and set at least `secret_key` (plus any other overrides you need).
- Optional DB seed/restore: create `./db_init/` and drop SQL files there; Podman runs them on first start.

## 4) First pod run (validate)

1) Ensure a volume exists for Postgres data: `podman volume create app-db-pvc`
2) Start the pod for a test run: `podman kube play app-pod.yaml`
3) Stop the test pod once verified: `podman kube down app-pod.yaml`

## 5) Quadlet service

1) Edit `app-pod.kube` so `Yaml=` points to your actual repo path (current value is a placeholder).
2) Copy `app-pod.kube` and `app.network` into `~/.config/containers/systemd` (create the directory if needed).
3) Reload systemd: `systemctl --user daemon-reload`
4) Start and enable the service: `systemctl --user enable --now app-pod.service`
5) If the unit doesn't appear, inspect the generated systemd with `/usr/libexec/podman/quadlet --user --dryrun`

## Notes and verification

- Check status/logs: `systemctl --user status app-pod.service` and `journalctl --user -u app-pod.service -f`
- Default ports: API `10101`, web `10102`; adjust host ports in `app-pod.yaml` if needed.
- If you change image tags, also update the `image:` fields in `app-pod.yaml`.
