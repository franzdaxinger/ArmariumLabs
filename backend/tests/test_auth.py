from backend.app.auth import create_remember_token, verify_remember_token


def test_remember_token_roundtrip(settings):
    token = create_remember_token("admin", settings)

    assert verify_remember_token(token, settings) == "admin"


def test_remember_token_rejects_wrong_user(settings):
    token = create_remember_token("other", settings)

    assert verify_remember_token(token, settings) is None
