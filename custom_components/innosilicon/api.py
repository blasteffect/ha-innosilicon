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

    async def _post(self, endpoint: str, *, json: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.jwt:
            await self.authenticate()

        for attempt in range(2):
            try:
                async with self.session.post(
                    f"{self.host}/api/{endpoint}",
                    json=json,
                    data=data,
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
                    result = await response.json(content_type=None)
            except InnosiliconAuthError:
                raise
            except (ClientError, asyncio.TimeoutError, ValueError) as err:
                raise InnosiliconApiError(str(err)) from err

            if result.get("success", False):
                return result
            if result.get("token") == "expired" and attempt == 0:
                self.jwt = None
                await self.authenticate()
                continue
            raise InnosiliconApiError(result.get("message") or "Miner returned success=false")

        raise InnosiliconApiError(f"Unable to call {endpoint}")

    async def summary(self) -> dict[str, Any]:
        return await self._post("summary", json={})

    async def ping(self) -> bool:
        await self._post("ping", json={})
        return True

    async def reboot(self) -> None:
        await self._post("reboot", json={})

    async def update_pools(self, pools: list[dict[str, str]]) -> None:
        payload: dict[str, str] = {}
        for idx, pool in enumerate(pools[:3], start=1):
            payload[f"Pool{idx}"] = pool.get("url", "")
            payload[f"UserName{idx}"] = pool.get("username", "")
            payload[f"Password{idx}"] = pool.get("password", "")
        await self._post("updatePools", data=payload)
