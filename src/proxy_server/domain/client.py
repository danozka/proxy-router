from asyncio import StreamReader, StreamWriter

from proxy_server.domain.connection import Connection


class Client(Connection):
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        timeout_seconds: float = 2.0,
        buffer_size_bytes: int = 4096
    ) -> None:
        self._reader = reader
        self._writer = writer
        self._timeout_seconds = timeout_seconds
        self._buffer_size_bytes = buffer_size_bytes

    def __str__(self) -> str:
        return self.__class__.__name__
