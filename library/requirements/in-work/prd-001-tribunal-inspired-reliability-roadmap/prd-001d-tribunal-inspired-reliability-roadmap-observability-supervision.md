# PRD-001d: Observability and Voice-Session Supervision

> **Status:** Backlog
> **Priority:** P1
> **Effort:** XL (> 3d)
> **Schema changes:** Additive
> **Depends on:** PRD-001c

## Overview

Activate vendor-neutral distributed tracing, add bounded domain metrics, and formalize one supervisor for each voice session so leaks, duplicate finalization, unexplained latency, and non-terminal calls become detectable and recoverable.

## Goals

- Trace a call across ingress, providers, tools, persistence, and finalization.
- Measure latency, reliability, and outcome signals without exposing personal data.
- Guarantee voice-session cleanup and exactly-once terminal processing.

## Non-Goals

- Selecting a proprietary observability vendor in code.
- Recording prompts, transcripts, phone numbers, or raw provider payloads as telemetry attributes.
- Replacing product analytics with Prometheus metrics.

## Requirements

### OpenTelemetry

Use the existing settings in `backend/app/core/config.py` to gate setup.

Instrument:

- FastAPI request handling.
- HTTPX outbound provider calls.
- SQLAlchemy.
- Redis.
- Relevant WebSocket and voice pipeline stages with manual spans.

Resource attributes should include bounded service name, deployment environment, and release/commit identifier. Exclude health and metrics probes. Configure export through standard OTLP environment variables.

### Domain metrics

Define low-cardinality counters/histograms for:

- Calls started, connected, completed, and failed by bounded outcome.
- Call duration.
- Time to first transcript.
- Time to first agent audio.
- STT, LLM, TTS, and provider API latency.
- Interruption/barge-in count.
- Provider reconnect attempts and exhaustion.
- Tool-call duration and bounded outcome.
- Webhook verification and duplicate-delivery counts.
- Worker processing, retry, DLQ, and circuit-breaker state.
- Usage-limit rejection.
- RAG retrieval duration and bounded result quality signal.

Prohibit raw user input, contact IDs, phone numbers, transcripts, prompts, URLs, exception messages, and unconstrained provider values in labels.

### Voice-session supervisor

One supervisor owns the lifetime of each call:

- Cancellation propagation.
- Maximum session and idle timeout.
- WebSocket closure and task cleanup.
- Provider reconnect budget.
- Tool-call timeout and cancellation.
- Recording/transcript finalization.
- Exactly-once usage finalization.
- Exactly-once terminal call status.
- Recovery when a provider terminal event is missing or duplicated.

### Health model

- Liveness indicates process viability.
- Readiness checks critical startup dependencies without making all optional providers mandatory.
- Metrics and traces distinguish dependency degradation from Ring Rookie failures.

## Acceptance criteria

- [ ] Setting an OTLP endpoint activates tracing; leaving it unset adds no export dependency to local tests.
- [ ] A call trace links ingress, STT, LLM, tool, TTS, database, and terminal processing spans.
- [ ] Metrics expose no prohibited personal or high-cardinality labels.
- [ ] Disconnect, timeout, cancellation, and duplicate terminal-event tests leave no leaked tasks or sockets.
- [ ] Usage and terminal call state finalize exactly once under retries and reconnects.
- [ ] Provider degradation can be identified from traces, circuit state, and bounded latency/error metrics.
- [ ] Operational dashboards and alert thresholds are documented using the emitted signals.

## Verification

- Export traces to a local OTLP collector and inspect one complete synthetic call.
- Run telemetry cardinality/privacy tests against metric labels and span attributes.
- Force client disconnect, provider disconnect, tool timeout, and missing terminal webhook scenarios.
- Confirm health probes do not dominate traces or metrics.

## Ring Rookie evidence

- `backend/app/core/config.py` defines OTEL settings without application instrumentation.
- Sentry initialization exists in `backend/app/main.py`, but distributed provider/database/Redis tracing and voice-domain metrics were not found.
- Existing call and usage models provide places to anchor supervised terminal state.

## Tribunal architectural references

- `backend/app/core/telemetry.py`
- `backend/app/core/metrics.py`
- `backend/tests/voice_ws/test_call_supervisor.py`
- `backend/tests/voice_ws/test_connection_limits.py`
- `backend/tests/voice_ws/test_voice_bridge.py`
- `backend/tests/services/ai/test_voice_session_factory.py`

Do not copy these proprietary files; design Ring Rookie's telemetry attributes, metrics, and supervisor around its Pipecat, Deepgram, ElevenLabs, OpenAI Realtime, and Telnyx/Twilio paths.
