from datetime import datetime
from enum import Enum
from typing import List

import jwt
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from pydantic.alias_generators import to_camel


class Region(str, Enum):
    CHINA = 'China'
    EUROPE = 'Europe'
    NORTH_AMERICA = 'NorthAmerica'
    ASIA_PACIFIC = 'AsiaPacific'
    OTHER = 'Other'

    def is_china(self) -> bool:
        return self == Region.CHINA

    def base_url(self) -> str:
        if self.is_china():
            return "https://api.bambulab.cn/v1"
        return "https://api.bambulab.com/v1"


class Device(BaseModel):
    name: str
    online: bool
    dev_id: str
    print_status: str
    nozzle_diameter: float
    dev_model_name: str
    dev_access_code: str
    dev_product_name: str

    async def get_bambu_camera_url(self, client) -> HttpUrl:
        url = f"{client.region.base_url()}/iot-service/api/user/ttcode"
        headers = {
            "Authorization": f"Bearer {client.auth_token.jwt}",
            "user-id": client.auth_token.username
        }
        response = await client._send_request('post', url, headers=headers, json={"dev_id": self.dev_id})
        ttcode = response['ttcode']
        authkey = response['authkey']
        passwd = response['passwd']
        region = response['region']

        # no idea on how to use the streaming url but I migrated the code as is from the rust package
        return HttpUrl.build(scheme="bambu", host=f"/{ttcode}", query=f"authkey={authkey}&passwd={passwd}&region={region}")


class Task(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, protected_namespaces=())
    id: int
    design_id: int
    design_title: str
    instance_id: int
    model_id: str
    title: str
    cover: HttpUrl
    status: int
    feedback_status: int
    start_time: datetime
    end_time: datetime
    weight: float
    length: int
    cost_time: int
    profile_id: int
    plate_index: int
    plate_name: str
    device_id: str
    ams_detail_mapping: List['AMSDetail']
    mode: str
    is_public_profile: bool
    is_printable: bool
    device_model: str
    device_name: str
    bed_type: str


class AMSDetail(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    position: int = 0
    source_color: str
    target_color: str
    filament_id: str
    filament_type: str
    target_filament_type: str
    weight: float


class Personal(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    bio: str
    links: List[HttpUrl]
    task_weight_sum: float
    task_length_sum: int
    task_time_sum: int
    background_url: HttpUrl


class Account(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    uid: int
    uid_str: str
    account: str
    name: str
    avatar: HttpUrl
    fan_count: int
    follow_count: int
    identifier: int
    likeCount: int
    collection_count: int
    download_count: int
    product_models: List[str]
    personal: Personal
    is_nsfw_shown: int = Field(alias="isNSFWShown")
    my_like_count: int
    favorites_count: int
    default_license: str
    point: int


class Token(BaseModel):
    username: str
    jwt: str

    @classmethod
    def try_from(cls, jwt_token: str) -> 'Token':
        try:
            decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
            username = decoded_token.get('username')
            if not username:
                raise jwt.InvalidTokenError("Username not found in token")
            return cls(username=username, jwt=jwt_token)
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid JWT token: {str(e)}")


class LoginResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    access_token: str


class DevicesResponse(BaseModel):
    devices: List[Device]


class TasksResponse(BaseModel):
    total: int
    hits: List[Task]
