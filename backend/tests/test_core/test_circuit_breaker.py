import asyncio

import pytest

from app.core.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitConfig,
    CircuitState,
    ProviderUnavailableError,
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
