from pathlib import Path
from scripts.check_env_drift import backend_names, env_file, frontend_names


def test_env_file_ignores_comments_and_does_not_expose_values(tmp_path: Path):
    path = tmp_path / ".env.example"
    path.write_text("# comment\nTOKEN=super-secret\n")
    assert set(env_file(path)) == {"TOKEN"}


def test_backend_names_reads_annotated_settings(tmp_path: Path):
    path = tmp_path / "config.py"
    path.write_text("class Settings:\n    FOO: str = 'x'\n")
    assert backend_names(path) == {"FOO"}


def test_frontend_names_supports_both_access_forms(tmp_path: Path):
    (tmp_path / "x.ts").write_text(
        "process.env.NEXT_PUBLIC_API; process.env['SERVER_KEY']"
    )
    assert frontend_names(tmp_path) == {"NEXT_PUBLIC_API", "SERVER_KEY"}
