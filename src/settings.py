from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    basic_auth_user: str = Field(alias='BASIC_AUTH_USER', default='user')
    basic_auth_password: str = Field(alias='BASIC_AUTH_PASSWORD', default='password')
    logging_level: str = Field(alias='LOGGING_LEVEL', default='INFO')
    proxy_router_buffer_size_bytes: int = Field(alias='PROXY_ROUTER_BUFFER_SIZE_BYTES', default=4096)
    proxy_router_host: str = Field(alias='PROXY_ROUTER_HOST', default='0.0.0.0')
    proxy_router_port: int = Field(alias='PROXY_ROUTER_PORT', default=8888)
    proxy_router_timeout_seconds: float = Field(alias='PROXY_ROUTER_TIMEOUT_SECONDS', default=2.0)
