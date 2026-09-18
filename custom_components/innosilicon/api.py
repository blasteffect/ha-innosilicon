from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout


class InnosiliconApiError(Exception):
    pass


class InnosiliconAuthError(InnosiliconApiError):
    pass


class InnosiliconApi:
    def __init__(self, session: ClientSession, host: str, username: str, password: str) -> None:
        self.session = session
        self.host = host.rstrip("/")
        if not self.host.startswith(("http://", "https://")):
            self.host = f"http://{self.host}"
        self.username = username
        self.password = password
        self.jwt: str | None = None
        self._lock = asyncio.Lock()

    async def authenticate(self) -> None:
        async with self._lock:
            try:
                async with self.session.post(
                    f"{self.host}/api/auth",
                    data={"username": self.username, "password": self.password},
                    headers={"Accept": "application/json, text/plain, */*"},
                    timeout=ClientTimeout(total=10),
                    ssl=False,
                ) as response:
                    if response.status in (401, 403):
                        raise InnosiliconAuthError("Invalid username or password")
                    response.raise_for_status()
                    data = await response.json(content_type=None)
            except InnosiliconAuthError:
                raise
            except (ClientError, asyncio.TimeoutError, ValueError) as err:
                raise InnosiliconApiError(str(err)) from err

            if not data.get("success") or not data.get("jwt"):
                raise InnosiliconAuthError("Authentication failed")
            self.jwt = data["jwt"]

    async def summary(self) -> dict[str, Any]:
        if not self.jwt:
            await self.authenticate()

        for attempt in range(2):
            try:
                async with self.session.post(
                    f"{self.host}/api/summary",
                    json={},
                    headers={
                        "Accept": "application/json, text/plain, */*",
                        "Authorization": f"Bearer {self.jwt}",
                    },
                    timeout=ClientTimeout(total=10),
                    ssl=False,
                ) as response:
                    if response.status in (401, 403):
                        if attempt == 0:
                            self.jwt = None
                            await self.authenticate()
                            continue
                        raise InnosiliconAuthError("Authentication expired")
                    response.raise_for_status()
                    data = await response.json(content_type=None)
            except InnosiliconAuthError:
                raise
            except (ClientError, asyncio.TimeoutError, ValueError) as err:
                raise InnosiliconApiError(str(err)) from err

            if not data.get("success", False):
                raise InnosiliconApiError("Miner returned success=false")
            return data

        raise InnosiliconApiError("Unable to retrieve summary")
