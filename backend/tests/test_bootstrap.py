from pathlib import Path

from backend.app.services.bootstrap_service import bootstrap_armarium_root


def test_bootstrap_creates_external_layout_and_copies_missing_defaults(settings, tmp_path):
    seed = tmp_path / "seed"
    template = seed / "bauplaene" / "einfaches-werk"
    persona = seed / "personen" / "global"
    template.mkdir(parents=True)
    persona.mkdir(parents=True)
    (template / "README.md").write_text("template", encoding="utf-8")
    (persona / "schatzmeister.yaml").write_text("id: schatzmeister\n", encoding="utf-8")

    actions = bootstrap_armarium_root(settings, seed)

    assert settings.works_dir.is_dir()
    assert settings.scriptorium_dir.is_dir()
    assert (settings.templates_dir / "einfaches-werk" / "README.md").exists()
    assert (settings.personas_dir / "global" / "schatzmeister.yaml").exists()
    assert actions


def test_bootstrap_does_not_overwrite_existing_defaults(settings, tmp_path):
    seed = tmp_path / "seed"
    persona = seed / "personen" / "global"
    persona.mkdir(parents=True)
    (persona / "schatzmeister.yaml").write_text("id: new\n", encoding="utf-8")
    existing = settings.personas_dir / "global" / "schatzmeister.yaml"
    before = existing.read_text(encoding="utf-8")

    bootstrap_armarium_root(settings, seed)

    assert existing.read_text(encoding="utf-8") == before
