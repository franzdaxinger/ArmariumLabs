# Local Service

ArmariumLabs can run as a systemd user service. This is the recommended local setup on a Linux workstation.

## Install

From the repository root:

```bash
./scripts/install_user_service.sh
```

This does four things:

- prepares `.venv`, dependencies, bootstrap folders, and SQLite
- writes `~/.config/systemd/user/armariumlabs.service`
- enables the service for the user session
- links `~/.local/bin/ArmariumLabs` to `scripts/ArmariumLabs`

If `~/.local/bin` is not in your shell `PATH`, add it in your shell profile.

## Control

```bash
ArmariumLabs --status
ArmariumLabs --start
ArmariumLabs --stop
ArmariumLabs --restart
ArmariumLabs --logs
```

The service uses `Restart=on-failure`. If the server crashes, systemd starts it again after five seconds. If you run `ArmariumLabs --stop`, systemd treats that as an intentional stop and does not restart it.

## Autostart

The installer runs:

```bash
systemctl --user enable armariumlabs.service
```

This starts ArmariumLabs automatically with the user systemd session. On systems where user services only start after login, enable lingering manually:

```bash
loginctl enable-linger "$USER"
```

That command may require admin privileges depending on the system.
