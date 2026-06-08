# Usage

Start the local Bergfried:

```bash
./scripts/dev.sh
```

Open `http://localhost:8000`, log in, and create a new Werk.

## Fresh Clone Setup

The repository contains only the Bergfried core app and minimal seed files. Real Werke, custom Personen, logs, builds, uploads, and databases stay outside Git under `ARMARIUM_ROOT`.

Initialize the external layout manually:

```bash
python scripts/bootstrap.py
```

`./scripts/dev.sh` runs this bootstrap automatically before starting FastAPI. Existing files are left untouched.

If no environment variables are set, the local default is `admin` / `1`. This is only for first local startup and should be changed.

## Creating a Werk

The form accepts:

- Name
- Repo name / Work ID
- Idea
- Hard requirements
- Bauplan
- Personas

If Work ID is empty, ArmariumLabs derives it from the name. Work IDs may contain only lowercase letters, digits, and dashes.

Creating a Werk copies the selected Bauplan, creates the Skriptorium folder tree, initializes Git, writes initial docs, registers the Werk in SQLite, and redirects to the detail page.

## Reviews

Reviews are text-based. Every decision is stored in SQLite and appended to `docs/05_acceptance_log.md` inside the Werk repository.

Allowed decisions:

- `approve`
- `request_changes`
- `reject`
- `defer`
- `comment`
