import asyncio
import logging
from logging import Logger

from proxy_server.connection import Connection
from proxy_server.request_context import request_id_context


class Proxy(Connection):
    _log: Logger = logging.getLogger(__name__)
    _host: str
    _port: int

    def __init__(self, host: str, port: int, timeout_seconds: float = 2.0, buffer_size_bytes: int = 4096) -> None:
        self._host = host
        self._port = port
        super().__init__(timeout_seconds=timeout_seconds, buffer_size_bytes=buffer_size_bytes)

    async def connect(self) -> None:
        self._log.debug(f'[{request_id_context.get()}] Establishing connection with {self}...')
        self._reader, self._writer = await asyncio.open_connection(host=self._host, port=self._port)
        self._log.debug(f'[{request_id_context.get()}] Connection with {self} established')

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(host=\'{self._host}\', port={self._port})'
