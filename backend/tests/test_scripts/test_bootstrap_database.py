"""Regression tests for local database bootstrap metadata."""

import app.models  # noqa: F401
from app.db.base import Base


def test_bootstrap_metadata_includes_user_settings_table() -> None:
    """Ensure create_all includes the settings table required by dashboard APIs."""
    assert "user_settings" in Base.metadata.tables
