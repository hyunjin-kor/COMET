"""Bound uploaded/API bytes before parsers run in optional hosted mode."""

from starlette.responses import JSONResponse

from backend.config import settings

MAX_HOSTED_BODY_BYTES = 2 * 1024 * 1024


class HostedBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not settings.hosted_mode:
            return await self.app(scope, receive, send)
        parts, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body = message.get("body", b"")
            size += len(body)
            if size > MAX_HOSTED_BODY_BYTES:
                response = JSONResponse({"detail": "Request exceeds the 2 MiB service limit"}, status_code=413)
                return await response(scope, receive, send)
            parts.append(body)
            if not message.get("more_body", False):
                break
        delivered = False

        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(parts), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)
