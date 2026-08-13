"""Local callback relay matching the OAuth redirect registered by GG Coder."""

import asyncio
from urllib.parse import urlsplit

from app.core.config import settings

_relay_server: asyncio.AbstractServer | None = None
_relay_lock = asyncio.Lock()
HTTP_REQUEST_PARTS = 2


async def ensure_callback_relay() -> None:
    """Start a local one-shot-compatible relay on GG Coder's registered port."""
    global _relay_server
    async with _relay_lock:
        if _relay_server is not None and _relay_server.is_serving():
            return
        try:
            _relay_server = await asyncio.start_server(
                _handle_callback,
                host=settings.CHATGPT_OAUTH_RELAY_HOST,
                port=1455,
            )
        except OSError as exc:
            raise RuntimeError("OpenAI OAuth callback port 1455 is unavailable") from exc


async def _handle_callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Relay only the registered callback path to the FastAPI callback endpoint."""
    try:
        request_line = await asyncio.wait_for(reader.readline(), timeout=5)
        parts = request_line.decode(errors="replace").strip().split(" ")
        target = parts[1] if len(parts) >= HTTP_REQUEST_PARTS else ""
        parsed = urlsplit(target)
        if parsed.path != "/auth/callback":
            await _respond(writer, "404 Not Found", "Not found")
            return
        callback_url = settings.CHATGPT_OAUTH_APP_CALLBACK_URL
        if parsed.query:
            callback_url = f"{callback_url}?{parsed.query}"
        response = (
            "HTTP/1.1 303 See Other\r\n"
            f"Location: {callback_url}\r\n"
            "Cache-Control: no-store\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n\r\n"
        )
        writer.write(response.encode())
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def _respond(writer: asyncio.StreamWriter, status: str, body: str) -> None:
    payload = body.encode()
    writer.write(
        (
            f"HTTP/1.1 {status}\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            "Cache-Control: no-store\r\n"
            f"Content-Length: {len(payload)}\r\n"
            "Connection: close\r\n\r\n"
        ).encode()
        + payload
    )
    await writer.drain()
