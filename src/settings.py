from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    basic_auth_user: str = Field(alias='BASIC_AUTH_USER', default='user')
    basic_auth_password: str = Field(alias='BASIC_AUTH_PASSWORD', default='password')
    logging_level: str = Field(alias='LOGGING_LEVEL', default='INFO')
    proxy_routing_config_file_path: Path = Field(alias='PROXY_ROUTING_CONFIG_FILE_PATH', default='/app/routing.json')
    proxy_server_buffer_size_bytes: int = Field(alias='PROXY_SERVER_BUFFER_SIZE_BYTES', default=4096)
    proxy_server_host: str = Field(alias='PROXY_SERVER_HOST', default='0.0.0.0')
    proxy_server_port: int = Field(alias='PROXY_SERVER_PORT', default=8888)
    proxy_server_timeout_seconds: float = Field(alias='PROXY_SERVER_TIMEOUT_SECONDS', default=2.0)
