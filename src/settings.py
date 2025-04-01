from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    user: str = Field(alias='AUTH_USER', default='user')
    password: str = Field(alias='AUTH_PASSWORD', default='password')
    proxy_host: str = Field(alias='PROXY_HOST', default='127.0.0.1')
    proxy_port: int = Field(alias='PROXY_PORT', default=3128)
    host: str = Field(alias='HOST', default='127.0.0.1')
    port: int = Field(alias='PORT', default=8888)
    timeout_seconds: float = Field(alias='TIMEOUT_SECONDS', default=2.0)
    buffer_size_bytes: int = Field(alias='BUFFER_SIZE_BYTES', default=4096)
    logging_level: str = Field(alias='LOGGING_LEVEL', default='INFO')
