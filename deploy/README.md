# How to deploy with Podman

## 1. Containers

1. Use the `build.sh` script to build the container images. You can specify `api`, `web`, or `all` (default)
   as a parameter.

## 2. Secrets

1. Copy the example secrets YAML: `cp app-secrets{.example,}.yaml`.
2. Set restricted permissions on the secrets file: `chmod 600 app-secrets.yaml`.
3. Fill in the required fields in `app-secrets.yaml`:
    - `POSTGRES_USER`: Admin username for the Postgres container.
    - `POSTGRES_PASSWORD`: Admin password for the Postgres container.
    - `POSTGRES_DB`: Name of the Postgres database.
    - `DATABASE_URL`: Full connection string for the database.
4. Deploy the secrets: `podman kube play app-secrets.yaml`.

## 3. Pod

1. If you need to restore a database backup, create the directory `./db_init/` and place the SQL script
   inside.
2. Copy API example config: `cp ../app_api/config.example.toml api_config.toml` and set at least `secret_key`.
3. Start the pod with `podman kube play app-pod.yaml`.
4. If everything works correctly, stop the pod with `podman kube down app-pod.yaml` (the service will start
   the pod later).

## 4. Service

1. Ensure that the `Yaml` field in `app-pod.kube` points to the correct path of the pod YAML file.
2. Copy `app-pod.kube` and `app.network` to `~/.config/containers/systemd` (create the directory if it doesn't
   exist).
3. Reload systemd with `systemctl --user daemon-reload`.
4. Start the pod with `systemctl --user start app-pod.service`.
   If the service doesn't exist, check the unit creation with `/usr/libexec/podman/quadlet --user --dryrun`.

## 5. System Configuration

1. **Enable tmp.mount** (prevents Podman boot ID errors): `sudo systemctl enable tmp.mount`
2. **Enable user lingering** (allows user services to start at boot): `sudo loginctl enable-linger <username>`
   Verify lingering with `loginctl show-user <username> | grep Linger` (should output `Linger=yes`)
