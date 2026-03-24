"""
Bearer token authentication middleware.

If INTERNAL_API_KEY is set, all requests (except exempt paths) must include
Authorization: Bearer <key>. If unset, auth is disabled (local dev).
"""

import hmac
import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

EXEMPT_PATHS = {"/v2/health", "/health", "/", "/openapi.json", "/robots.txt"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.api_key = os.environ.get("INTERNAL_API_KEY")

    async def dispatch(self, request: Request, call_next):
        if not self.api_key:
            return await call_next(request)
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing Authorization: Bearer <key> header"},
            )
        token = auth[7:]
        if not hmac.compare_digest(token, self.api_key):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key"},
            )
        return await call_next(request)
