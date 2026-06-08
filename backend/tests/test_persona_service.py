from backend.app.services import persona_service


def test_load_personas(settings):
    personas = persona_service.load_personas(settings.personas_dir)
    assert len(personas) == 1
    assert personas[0]["id"] == "schatzmeister"
    assert personas[0]["regeln"] == ["Einfach halten."]
