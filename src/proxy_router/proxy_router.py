import asyncio
import base64
import logging
from asyncio import Server, StreamReader, StreamWriter
from logging import Logger
from uuid import uuid4

from proxy_router.request import Request
from proxy_router.request_adapter import RequestAdapter
from proxy_router.request_context import request_id_context


class ProxyRouter:
    _log: Logger = logging.getLogger(__name__)
    _encoded_credentials: str
    _proxy_host: str
    _proxy_port: int
    _host: str
    _port: int
    _timeout_seconds: float
    _buffer_size_bytes: int
    _request_adapter: RequestAdapter

    def __init__(
        self,
        user: str,
        password: str,
        proxy_host: str,
        proxy_port: int,
        host='127.0.0.1',
        port=8888,
        timeout_seconds: float = 2.0,
        buffer_size_bytes: int = 4096,
        request_adapter: RequestAdapter = RequestAdapter()
    ) -> None:
        self._encoded_credentials = base64.b64encode(f'{user}:{password}'.encode()).decode()
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        self._host = host
        self._port = port
        self._timeout_seconds = timeout_seconds
        self._buffer_size_bytes = buffer_size_bytes
        self._request_adapter = request_adapter

    async def start(self) -> None:
        self._log.info('Starting server...')
        server: Server = await asyncio.start_server(
            client_connected_cb=self._handle_request,
            host=self._host,
            port=self._port
        )
        async with server:
            self._log.info(f'Server is running on http://{self._host}:{self._port}')
            await server.serve_forever()

    async def _handle_request(self, client_reader: StreamReader, client_writer: StreamWriter) -> None:
        request_id_context.set(uuid4())
        self._log.info(f'[{request_id_context.get()}] Handling new request...')
        try:
            request: Request | None = self._request_adapter.adapt_request_from_bytes(
                await asyncio.wait_for(
                    fut=client_reader.read(self._buffer_size_bytes),
                    timeout=self._timeout_seconds
                )
            )
            if not request:
                return
            request.headers['Proxy-Authorization'] = f'Basic {self._encoded_credentials}'
            self._log.info(f'[{request_id_context.get()}] Handling {request}...')
            server_reader: StreamReader
            server_writer: StreamWriter
            server_reader, server_writer = await self._open_connection_with_proxy(request)
            if request.is_https():
                await asyncio.gather(
                    self._tunnel_data(reader=client_reader, writer=server_writer),
                    self._tunnel_data(reader=server_reader, writer=client_writer)
                )
            else:
                await self._tunnel_data(reader=server_reader, writer=client_writer)
            self._log.info(f'[{request_id_context.get()}] Request handled')
        except Exception as ex:
            self._log.error(f'[{request_id_context.get()}] Error handling request: {ex.__class__.__name__} - {ex}')
        finally:
            client_writer.close()
            await client_writer.wait_closed()

    async def _open_connection_with_proxy(self, request: Request) -> tuple[StreamReader, StreamWriter]:
        self._log.debug(
            f'[{request_id_context.get()}] Establishing connection with \'{self._proxy_host}:{self._proxy_port}\'...'
        )
        server_reader: StreamReader
        server_writer: StreamWriter
        server_reader, server_writer = await asyncio.open_connection(host=self._proxy_host, port=self._proxy_port)
        server_writer.write(self._request_adapter.adapt_request_to_bytes(request))
        await server_writer.drain()
        self._log.debug(
            f'[{request_id_context.get()}] Connection with \'{self._proxy_host}:{self._proxy_port}\' established'
        )
        return server_reader, server_writer

    async def _tunnel_data(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._log.debug(f'[{request_id_context.get()}] Tunneling data...')
        while True:
            try:
                data: bytes = await asyncio.wait_for(
                    fut=reader.read(self._buffer_size_bytes),
                    timeout=self._timeout_seconds
                )
                if not data:
                    break
                writer.write(data)
                await writer.drain()
            except TimeoutError:
                break
        self._log.debug(f'[{request_id_context.get()}] Tunneling data completed')
