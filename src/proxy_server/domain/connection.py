import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from logging import Logger


class Connection:
    _log: Logger = logging.getLogger(__name__)
    _reader: StreamReader | None = None
    _writer: StreamWriter | None = None
    _timeout_seconds: float = 60.0
    _buffer_size_bytes: int = 4096

    async def read(self) -> bytes | None:
        if self._reader is None:
            raise NotImplementedError('No reader was found')
        else:
            try:
                return await asyncio.wait_for(
                    fut=self._reader.read(self._buffer_size_bytes),
                    timeout=self._timeout_seconds
                )
            except TimeoutError:
                self._log.debug('TimeoutError raised on bytes stream reading')
                return None

    async def write(self, data: bytes) -> None:
        if self._writer is None:
            raise NotImplementedError('No writer was found')
        else:
            try:
                self._writer.write(data)
                await self._writer.drain()
            except ConnectionError:
                self._log.debug('ConnectionError raised on bytes stream writing')

    async def close(self) -> None:
        if self._writer is None:
            raise NotImplementedError('No writer was found')
        else:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except ConnectionError:
                self._log.debug('ConnectionError raised on bytes stream closing')
