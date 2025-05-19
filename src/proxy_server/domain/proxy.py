import asyncio
import logging
from logging import Logger

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from proxy_server.domain.connection import Connection


class Proxy(Connection, BaseModel):
    _log: Logger = logging.getLogger(__name__)
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    id: str
    hostname: str = Field(repr=False)
    port: int = Field(repr=False)
    authentication_id: str = Field(repr=False)

    async def connect(self, timeout_seconds: float = 60.0, buffer_size_bytes: int = 4096) -> None:
        self._log.debug(f'Establishing connection with {self}...')
        self._reader, self._writer = await asyncio.open_connection(host=self.hostname, port=self.port)
        self._timeout_seconds = timeout_seconds
        self._buffer_size_bytes = buffer_size_bytes
        self._log.debug(f'Connection with {self} established')

    def __str__(self) -> str:
        return self.__repr__()
