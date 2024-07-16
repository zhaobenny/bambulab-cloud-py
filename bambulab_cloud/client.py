from typing import Any, Dict, List, Optional

import httpx
from pydantic import ValidationError

from bambulab_cloud.models import (Account, Device, DevicesResponse,
                                   LoginResponse, Region, Task, TasksResponse,
                                   Token)


class LoginError(Exception):
    pass


class BambuClient:
    def __init__(self, auth_token: Token, region: Region):
        self.region = region
        self.auth_token = auth_token
        self._client = httpx.AsyncClient()

    @classmethod
    async def login(cls, email: str, password: str, region=Region.NORTH_AMERICA) -> 'BambuClient':
        url = f"{region.base_url()}/user-service/user/login"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"account": email, "password": password})
            response.raise_for_status()
            response_data = response.json()
        try:
            login_response = LoginResponse(**response_data)
        except ValidationError as e:
            raise LoginError(f"Failed to parse login response: {str(e)}")

        return cls(Token.try_from(login_response.access_token), region=region)

    async def get_profile(self) -> Account:
        url = f"{self.region.base_url()}/user-service/my/profile"
        response = await self._send_request('get', url, headers={"Authorization": f"Bearer {self.auth_token.jwt}"})
        return Account(**response)

    async def get_devices(self) -> List[Device]:
        url = f"{self.region.base_url()}/iot-service/api/user/bind"
        response = await self._send_request('get', url, headers={"Authorization": f"Bearer {self.auth_token.jwt}"})
        devices_response = DevicesResponse(**response)
        return devices_response.devices

    async def get_tasks(self, only_device: Optional[str] = None) -> List[Task]:
        url = f"{self.region.base_url()}/user-service/my/tasks"
        params = {"limit": "500", "deviceId": only_device or ""}
        response = await self._send_request(
            'get', url, headers={"Authorization": f"Bearer {self.auth_token.jwt}"}, params=params)
        tasks_response = TasksResponse(**response)
        return tasks_response.hits

    @property
    def mqtt_host(self) -> str:
        return "cn.mqtt.bambulab.com" if self.region.is_china() else "us.mqtt.bambulab.com"

    async def _send_request(self, method: str, url: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        response = await self._client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _close(self) -> None:
        await self._client.aclose()
