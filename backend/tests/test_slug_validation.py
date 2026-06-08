from backend.app.services.filesystem_service import ValidationError, slugify_work_id, validate_work_id


def test_slugify_work_id():
    assert slugify_work_id("Todo App!") == "todo-app"


def test_slugify_work_id_transliterates_german_umlauts():
    assert slugify_work_id("Schöne Bücher fürs Büro") == "schoene-buecher-fuers-buero"


def test_validate_work_id_accepts_lowercase_digits_and_dashes():
    assert validate_work_id("todo-app-1") == "todo-app-1"


def test_validate_work_id_rejects_invalid_values():
    for value in ["Todo", "todo_app", "-todo", "todo-", "todo--app", ""]:
        try:
            validate_work_id(value)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"expected invalid: {value}")
