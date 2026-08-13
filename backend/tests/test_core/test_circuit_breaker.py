import asyncio

import httpx
import pytest

from app.core.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitBreakerRegistry,
    CircuitConfig,
    CircuitState,
    ProviderUnavailableError,
    is_transient_provider_failure,
)


@pytest.mark.asyncio
async def test_open_half_open_and_recovery() -> None:
    now = [0.0]
    breaker = AsyncCircuitBreaker("telnyx", CircuitConfig(1, 10), clock=lambda: now[0])

    async def fail() -> None:
        raise TimeoutError

    with pytest.raises(TimeoutError):
        await breaker.call(fail)
    assert breaker.state is CircuitState.OPEN
    with pytest.raises(ProviderUnavailableError):
        await breaker.call(fail)
    now[0] = 11

    entered = asyncio.Event()
    release = asyncio.Event()

    async def probe() -> str:
        entered.set()
        await release.wait()
        return "ok"

    task = asyncio.create_task(breaker.call(probe))
    await entered.wait()
    with pytest.raises(ProviderUnavailableError):
        await breaker.call(probe)
    release.set()
    assert await task == "ok"
    assert breaker.state is CircuitState.CLOSED


@pytest.mark.asyncio
async def test_deterministic_failure_is_excluded() -> None:
    breaker = AsyncCircuitBreaker("openai", CircuitConfig(1, 1))

    async def invalid() -> None:
        raise ValueError("invalid request")

    with pytest.raises(ValueError, match="invalid request"):
        await breaker.call(invalid)
    assert breaker.state is CircuitState.CLOSED


@pytest.mark.asyncio
async def test_cancellation_does_not_increment_failures() -> None:
    breaker = AsyncCircuitBreaker("telnyx", CircuitConfig(2, 1))

    async def cancelled() -> None:
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await breaker.call(cancelled)
    assert breaker.failures == 0
    assert breaker.state is CircuitState.CLOSED


def test_httpx_classification_and_registry_duplicates() -> None:
    request = httpx.Request("GET", "https://provider.test")
    assert is_transient_provider_failure(httpx.ConnectError("offline", request=request))
    assert is_transient_provider_failure(
        httpx.HTTPStatusError(
            "busy", request=request, response=httpx.Response(429, request=request)
        )
    )
    assert not is_transient_provider_failure(
        httpx.HTTPStatusError(
            "auth", request=request, response=httpx.Response(401, request=request)
        )
    )
    registry = CircuitBreakerRegistry()
    first = registry.register("telnyx", CircuitConfig(2, 1))
    assert registry.register("telnyx", CircuitConfig(2, 1)) is first
    with pytest.raises(ValueError, match="different"):
        registry.register("telnyx", CircuitConfig(3, 1))
