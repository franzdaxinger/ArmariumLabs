# ArmariumLabs

ArmariumLabs v0.1 is a local app factory for non-technical users. The Bergfried manages Werke, shows their pipeline phase, creates new projects from Bauplaene, and records text-based Abnahmen.

The app is intentionally small:

- Backend: FastAPI
- UI: server-rendered Jinja2 templates
- Database: SQLite in this core repository, ignored by Git
- Auth: one local admin user
- CLI: `scripts/armarium_cli.py`

## Start

```bash
./scripts/dev.sh
```

Then open `http://localhost:8000`.

On a fresh clone, `dev.sh` also initializes the external local folder layout under `ARMARIUM_ROOT`:

- `werke/`
- `skriptorium/`
- `bauplaene/`
- `personen/`

It copies only missing default seed files from `seed/` and never overwrites existing works, templates, or personas.

Manual bootstrap:

```bash
python scripts/bootstrap.py
```

Default login, if no environment variables are set:

- username: `admin`
- password: `1`

Change this for real local use:

```bash
export ARMARIUM_ADMIN_USERNAME="admin"
export ARMARIUM_ADMIN_PASSWORD="change-me"
export ARMARIUM_SESSION_SECRET="change-this-secret"
```

## Test

```bash
./scripts/run_tests.sh
```

Tests use temporary directories and do not modify your real `~/ArmariumLabs`.

## CLI

```bash
python scripts/armarium_cli.py list
python scripts/armarium_cli.py create-work --name "Todo App" --work-id "todo-app" --idea "Simple todo app"
python scripts/armarium_cli.py show todo-app
python scripts/armarium_cli.py set-phase todo-app review
python scripts/armarium_cli.py add-review todo-app --decision approve --comment "Freigegeben"
python scripts/armarium_cli.py status todo-app
```

## Terms

- Bergfried: ArmariumLabs control center
- Werke: app projects
- Skriptorium: large files, databases, logs, and builds
- Bauplaene: templates for new works
- Personen: reusable rules and perspectives
- Abnahme: review
- Lagebericht: review or status report
