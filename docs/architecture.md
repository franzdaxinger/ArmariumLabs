# Architecture

ArmariumLabs v0.1 is a local FastAPI app with server-rendered HTML.

## Boundaries

- The web GUI and CLI both call the same service modules.
- Business logic lives in `backend/app/services`.
- SQLite is accessed directly through small helper functions, without an ORM.
- Werke are separate local Git repositories under `$ARMARIUM_ROOT/werke`.
- Large project data belongs under `$ARMARIUM_ROOT/skriptorium`.
- Bauplaene and Personen are read from `$ARMARIUM_ROOT/bauplaene` and `$ARMARIUM_ROOT/personen`.
- Minimal default Bauplaene and Personen live in `seed/` so a fresh Git clone can bootstrap a usable local root.

## Service Responsibilities

- `filesystem_service`: Work ID validation, template copy, file writes, scriptorium folders.
- `git_service`: local Git init, commit, status.
- `persona_service`: load YAML personas.
- `project_service`: create works, list works, phase changes.
- `review_service`: store reviews and append acceptance logs.
- `bootstrap_service`: create the external folder layout and copy missing seed defaults.

## Pipeline Phases

- `ideation`
- `requirements_definition`
- `test_plan_definition`
- `build_phase`
- `review`
- `acceptance`

## Deliberately Not Included

ArmariumLabs v0.1 has no real AI integration, no Codex orchestration, no cloud, no CI/CD, no mobile app, no multi-agent system, and no complex role model.
