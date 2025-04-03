import asyncio
import logging
from asyncio import Server, StreamReader, StreamWriter
from logging import Logger
from uuid import uuid4

from proxy_server.client import Client
from proxy_server.connection import Connection
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
        client: Client | None = None
        proxy: Proxy | None = None
        request_id_context.set(uuid4())
        self._log.info('Handling new request...')
        try:
            client: Client = Client(
                reader=client_reader,
                writer=client_writer,
                timeout_seconds=self._timeout_seconds,
                buffer_size_bytes=self._buffer_size_bytes
            )
            request: Request | None = self._request_adapter.adapt_request_from_bytes(await client.read())
            if not request:
                raise EmptyRequestException
            self._log.info(f'Handling {request}...')
            if self._request_authentication_adder is not None:
                self._request_authentication_adder.add_authentication_to_request(request)
            proxy: Proxy = await self._proxy_router.route_request_to_proxy(request)
            await proxy.connect()
            await proxy.write(self._request_adapter.adapt_request_to_bytes(request))
            if request.method == RequestMethod.connect:
                await asyncio.gather(
                    self._tunnel_data(source=client, destination=proxy),
                    self._tunnel_data(source=proxy, destination=client)
                )
            else:
                await self._tunnel_data(source=proxy, destination=client)
            self._log.info('Request handled successfully')
        except Exception as ex:
            self._log.error(f'Error handling request: {ex.__class__.__name__} - {ex}')
        finally:
            if client is not None:
                await client.close()
            if proxy is not None:
                await proxy.close()

    async def _tunnel_data(self, source: Connection, destination: Connection) -> None:
        self._log.debug(f'Tunneling data from {source} to {destination}...')
        while True:
            data: bytes = await source.read()
            if not data:
                break
            await destination.write(data)
        self._log.debug(f'Tunneling data from {source} to {destination} completed')
