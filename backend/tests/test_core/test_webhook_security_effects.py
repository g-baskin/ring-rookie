"""Signature edge cases required by the effect pipeline."""

import base64
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.core.webhook_security import validate_telnyx_signature, validate_twilio_signature


def test_twilio_valid_missing_and_malformed_signatures() -> None:
    import hashlib
    import hmac

    url = "https://example.test/webhooks/twilio/status"
    params = {"CallSid": "CA_SANITIZED", "CallStatus": "completed"}
    token = "sanitized-token"
    data = url + "".join(f"{key}{value}" for key, value in sorted(params.items()))
    signature = base64.b64encode(
        hmac.new(token.encode(), data.encode(), hashlib.sha1).digest()
    ).decode()

    assert validate_twilio_signature(signature, url, params, token)
    assert not validate_twilio_signature("", url, params, token)
    assert not validate_twilio_signature("malformed", url, params, token)


def test_telnyx_valid_stale_and_malformed_timestamp() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    encoded_public_key = base64.b64encode(public_key).decode()
    payload = b'{"data":{"id":"evt_sanitized","event_type":"unknown"}}'
    timestamp = str(int(time.time()))
    signature = base64.b64encode(private_key.sign(timestamp.encode() + b"|" + payload)).decode()

    assert validate_telnyx_signature(signature, timestamp, payload, encoded_public_key)
    stale = str(int(time.time()) - 301)
    stale_signature = base64.b64encode(private_key.sign(stale.encode() + b"|" + payload)).decode()
    assert not validate_telnyx_signature(stale_signature, stale, payload, encoded_public_key)
    assert not validate_telnyx_signature(signature, "not-a-timestamp", payload, encoded_public_key)
    assert not validate_telnyx_signature("malformed", timestamp, payload, encoded_public_key)
