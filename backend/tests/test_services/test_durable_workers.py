import pytest

from app.services.durable_workers import item_digest, redact_error, retry_delay, safe_payload_ref


def test_retry_full_jitter_is_deterministic_and_capped() -> None:
    assert retry_delay(3, base=2, cap=100, rng=lambda: 0.5) == 4
    assert retry_delay(99, base=2, cap=100, rng=lambda: 1) == 100


def test_identity_and_safe_reference() -> None:
    assert item_digest("contact-1") == item_digest("contact-1")
    assert safe_payload_ref("campaign-contact:abc_123") == "campaign-contact:abc_123"
    for unsafe in ("+15551234567", "prompt text", "https://example.test?a=secret"):
        with pytest.raises(ValueError, match="opaque"):
            safe_payload_ref(unsafe)


def test_exception_data_is_not_persisted() -> None:
    kind, message = redact_error(ConnectionError("token phone +15551234567"))
    assert kind == "ConnectionError"
    assert "token" not in message
    assert "+1555" not in message
