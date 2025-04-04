import asyncio
from asyncio import StreamReader, StreamWriter


class Connection:
    _reader: StreamReader | None = None
    _writer: StreamWriter | None = None
    _timeout_seconds: float = 2.0
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
                return None

    async def write(self, data: bytes) -> None:
        if self._writer is None:
            raise NotImplementedError('No writer was found')
        else:
            try:
                self._writer.write(data)
                await self._writer.drain()
            except ConnectionError:
                pass

    async def close(self) -> None:
        if self._writer is None:
            raise NotImplementedError('No writer was found')
        else:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except ConnectionError:
                pass
