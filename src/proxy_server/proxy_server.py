import asyncio
import logging
from asyncio import Server, StreamReader, StreamWriter
from logging import Logger
from uuid import uuid4

from proxy_server.empty_request_exception import EmptyRequestException
from proxy_server.i_proxy_router import IProxyRouter
from proxy_server.i_request_authentication_adder import IRequestAuthenticationAdder
from proxy_server.proxy import Proxy
from proxy_server.request import Request
from proxy_server.request_adapter import RequestAdapter
from proxy_server.request_context import request_id_context
from proxy_server.request_method import RequestMethod


class ProxyServer:
    _log: Logger = logging.getLogger(__name__)
    _proxy_router: IProxyRouter
    _host: str
    _port: int
    _timeout_seconds: float
    _buffer_size_bytes: int
    _request_adapter: RequestAdapter
    _request_authentication_adder: IRequestAuthenticationAdder | None

    def __init__(
        self,
        proxy_router: IProxyRouter,
        host='0.0.0.0',
        port=8888,
        timeout_seconds: float = 2.0,
        buffer_size_bytes: int = 4096,
        request_adapter: RequestAdapter = RequestAdapter(),
        request_authentication_adder: IRequestAuthenticationAdder | None = None
    ) -> None:
        self._proxy_router = proxy_router
        self._host = host
        self._port = port
        self._timeout_seconds = timeout_seconds
        self._buffer_size_bytes = buffer_size_bytes
        self._request_adapter = request_adapter
        self._request_authentication_adder = request_authentication_adder

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
        server_reader: StreamReader
        server_writer: StreamWriter | None = None
        self._log.info(f'[{request_id_context.get()}] Handling new request...')
        try:
            request: Request | None = self._request_adapter.adapt_request_from_bytes(
                await asyncio.wait_for(
                    fut=client_reader.read(self._buffer_size_bytes),
                    timeout=self._timeout_seconds
                )
            )
            if not request:
                raise EmptyRequestException
            self._log.info(f'[{request_id_context.get()}] Handling {request}...')
            if self._request_authentication_adder is not None:
                self._request_authentication_adder.add_authentication_to_request(request)
            proxy: Proxy = await self._proxy_router.route_request_to_proxy(request)
            server_reader, server_writer = await self._establish_connection_with_proxy(proxy=proxy, request=request)
            if request.method == RequestMethod.connect:
                await asyncio.gather(
                    self._tunnel_data(
                        source='client',
                        destination='proxy',
                        reader=client_reader,
                        writer=server_writer
                    ),
                    self._tunnel_data(
                        source='proxy',
                        destination='client',
                        reader=server_reader,
                        writer=client_writer
                    )
                )
            else:
                await self._tunnel_data(
                    source='proxy',
                    destination='client',
                    reader=server_reader,
                    writer=client_writer
                )
            self._log.info(f'[{request_id_context.get()}] Request handled successfully')
        except Exception as ex:
            self._log.error(f'[{request_id_context.get()}] Error handling request: {ex.__class__.__name__} - {ex}')
        finally:
            client_writer.close()
            await client_writer.wait_closed()
            if server_writer is not None:
                server_writer.close()
                await server_writer.wait_closed()

    async def _establish_connection_with_proxy(
        self,
        proxy: Proxy,
        request: Request
    ) -> tuple[StreamReader, StreamWriter]:
        self._log.debug(f'[{request_id_context.get()}] Establishing connection with {proxy}...')
        server_reader: StreamReader
        server_writer: StreamWriter
        server_reader, server_writer = await asyncio.open_connection(host=proxy.host, port=proxy.port)
        server_writer.write(self._request_adapter.adapt_request_to_bytes(request))
        await server_writer.drain()
        self._log.debug(f'[{request_id_context.get()}] Connection with {proxy} established')
        return server_reader, server_writer

    async def _tunnel_data(self, source: str, destination: str, reader: StreamReader, writer: StreamWriter) -> None:
        self._log.debug(f'[{request_id_context.get()}] Tunneling data from {source} to {destination}...')
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
        self._log.debug(f'[{request_id_context.get()}] Tunneling data from {source} to {destination} completed')
