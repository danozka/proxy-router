from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    authentication_config_file_path: Path = Field(alias='AUTH_CONFIG_FILE_PATH', default='/app/auth.json')
    logging_level: str = Field(alias='LOGGING_LEVEL', default='INFO')
    proxy_config_file_path: Path = Field(alias='PROXY_CONFIG_FILE_PATH', default='/app/proxy.json')
    proxy_server_buffer_size_bytes: int = Field(alias='PROXY_SERVER_BUFFER_SIZE_BYTES', default=4096)
    proxy_server_host: str = Field(alias='PROXY_SERVER_HOST', default='0.0.0.0')
    proxy_server_port: int = Field(alias='PROXY_SERVER_PORT', default=8888)
    proxy_server_timeout_seconds: float = Field(alias='PROXY_SERVER_TIMEOUT_SECONDS', default=60.0)
    routing_config_file_path: Path = Field(alias='ROUTING_CONFIG_FILE_PATH', default='/app/routing.json')
