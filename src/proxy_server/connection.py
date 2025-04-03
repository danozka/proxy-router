import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from logging import Logger


class Connection:
    _log: Logger = logging.getLogger(__name__)
    _reader: StreamReader | None = None
    _writer: StreamWriter | None = None
    _timeout_seconds: float
    _buffer_size_bytes: int

    def __init__(self, timeout_seconds: float = 2.0, buffer_size_bytes: int = 4096) -> None:
        self._timeout_seconds = timeout_seconds
        self._buffer_size_bytes = buffer_size_bytes

    async def read(self) -> bytes | None:
        if self._reader is None:
            self._log.error('No reader was found')
        else:
            try:
                return await asyncio.wait_for(
                    fut=self._reader.read(self._buffer_size_bytes),
                    timeout=self._timeout_seconds
                )
            except TimeoutError:
                return None

    async def write(self, data: bytes) -> None:
        if self._writer is None:
            self._log.error('No writer was found')
        else:
            self._writer.write(data)
            await self._writer.drain()

    async def close(self) -> None:
        if self._writer is None:
            self._log.error('No writer was found')
        else:
            self._writer.close()
            await self._writer.wait_closed()
