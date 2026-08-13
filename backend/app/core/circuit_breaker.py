"""Concurrency-safe async circuit breakers for remote provider boundaries."""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass(frozen=True)
class CircuitConfig:
    failure_threshold: int = 5
    recovery_seconds: float = 30.0


class ProviderUnavailableError(RuntimeError):
    """Stable failure returned while a provider circuit is open."""

    def __init__(self, provider: str, retry_after: float) -> None:
        self.provider = provider
        self.retry_after = max(0.0, retry_after)
        super().__init__(f"provider {provider} temporarily unavailable")


class AsyncCircuitBreaker:
    def __init__(
        self,
        provider: str,
        config: CircuitConfig = CircuitConfig(),
        *,
        clock: Callable[[], float] = time.monotonic,
        failure_classifier: Callable[[BaseException], bool] | None = None,
        metric_hook: Callable[[str, CircuitState], None] | None = None,
    ) -> None:
        self.provider = provider
        self.config = config
        self._clock = clock
        self._classifier = failure_classifier or is_transient_provider_failure
        self._metric_hook = metric_hook
        self.state = CircuitState.CLOSED
        self.failures = 0
        self._opened_at = 0.0
        self._probe_active = False
        self._lock = asyncio.Lock()

    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        probe = await self._admit()
        try:
            result = await operation()
        except BaseException as exc:
            await self._finish(probe, failure=self._classifier(exc))
            raise
        await self._finish(probe, failure=False)
        return result

    async def _admit(self) -> bool:
        async with self._lock:
            now = self._clock()
            if self.state is CircuitState.OPEN:
                elapsed = now - self._opened_at
                if elapsed < self.config.recovery_seconds:
                    raise ProviderUnavailableError(
                        self.provider, self.config.recovery_seconds - elapsed
                    )
                self._transition(CircuitState.HALF_OPEN)
            if self.state is CircuitState.HALF_OPEN:
                if self._probe_active:
                    raise ProviderUnavailableError(self.provider, self.config.recovery_seconds)
                self._probe_active = True
                return True
            return False

    async def _finish(self, probe: bool, *, failure: bool) -> None:
        async with self._lock:
            if probe:
                self._probe_active = False
                if failure:
                    self._open()
                else:
                    self.failures = 0
                    self._transition(CircuitState.CLOSED)
            elif failure and self.state is CircuitState.CLOSED:
                self.failures += 1
                if self.failures >= self.config.failure_threshold:
                    self._open()

    def _open(self) -> None:
        self._opened_at = self._clock()
        self._transition(CircuitState.OPEN)

    def _transition(self, state: CircuitState) -> None:
        if self.state is state:
            return
        self.state = state
        logger.info(
            "provider_circuit_state", extra={"provider": self.provider, "state": state.value}
        )
        if self._metric_hook:
            self._metric_hook(self.provider, state)


def is_transient_provider_failure(exc: BaseException) -> bool:
    """Classify SDK-neutral transport failures; adapters may supply richer classifiers."""
    if isinstance(exc, (TimeoutError, ConnectionError, asyncio.TimeoutError)):
        return True
    status = getattr(exc, "status_code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    too_many_requests = 429
    server_error = 500
    return status == too_many_requests or (isinstance(status, int) and status >= server_error)


class CircuitBreakerRegistry:
    """Explicit registry: instantiate only providers used by an application boundary."""

    def __init__(self) -> None:
        self._breakers: dict[str, AsyncCircuitBreaker] = {}

    def register(
        self, provider: str, config: CircuitConfig = CircuitConfig()
    ) -> AsyncCircuitBreaker:
        breaker = AsyncCircuitBreaker(provider, config)
        self._breakers[provider] = breaker
        return breaker

    def get(self, provider: str) -> AsyncCircuitBreaker:
        return self._breakers[provider]
