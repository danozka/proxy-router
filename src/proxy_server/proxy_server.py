import asyncio
import logging
from asyncio import Server, StreamReader, StreamWriter
from contextvars import ContextVar
from logging import Logger
from pathlib import Path
from uuid import UUID, uuid4

from aiopath import AsyncPath
from pydantic import TypeAdapter

from proxy_server.domain.client import Client
from proxy_server.domain.connection import Connection
from proxy_server.domain.proxy import Proxy
from proxy_server.domain.request import Request
from proxy_server.domain.request_method import RequestMethod
from proxy_server.exceptions.empty_request_exception import EmptyRequestException
from proxy_server.exceptions.proxy_not_found_exception import ProxyNotFoundException
from proxy_server.request_adapter import RequestAdapter
from proxy_server.services.i_proxy_router import IProxyRouter
from proxy_server.services.i_request_authentication_adder import IRequestAuthenticationAdder


request_id_context: ContextVar[UUID | None] = ContextVar('request_id', default=None)


class ProxyServer:
    _log: Logger = logging.getLogger(__name__)
    _proxy_config_file_path: AsyncPath
    _proxy_router: IProxyRouter
    _host: str
    _port: int
    _timeout_seconds: float
    _buffer_size_bytes: int
    _request_adapter: RequestAdapter
    _request_authentication_adder: IRequestAuthenticationAdder | None

    def __init__(
        self,
        proxy_config_file_path: Path,
        proxy_router: IProxyRouter,
        host: str = '0.0.0.0',
        port: int = 8888,
        timeout_seconds: float = 2.0,
        buffer_size_bytes: int = 4096,
        request_adapter: RequestAdapter = RequestAdapter(),
        request_authentication_adder: IRequestAuthenticationAdder | None = None
    ) -> None:
        self._proxy_config_file_path = AsyncPath(proxy_config_file_path)
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
            client_connected_cb=self.handle_request,
            host=self._host,
            port=self._port
        )
        async with server:
            self._log.info(f'Server is running on http://{self._host}:{self._port}')
            await server.serve_forever()

    async def handle_request(self, client_reader: StreamReader, client_writer: StreamWriter) -> None:
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
            if request is None:
                raise EmptyRequestException
            self._log.info(f'Handling {request}...')
            proxy_id: str = await self._proxy_router.route_request_to_proxy(request)
            async with self._proxy_config_file_path.open(mode='r') as file:
                proxies: list[Proxy] = TypeAdapter(list[Proxy]).validate_json(await file.read())
            proxy = next((x for x in proxies if x.id == proxy_id), None)
            if proxy is None:
                raise ProxyNotFoundException(proxy_id)
            if self._request_authentication_adder is not None:
                await self._request_authentication_adder.add_authentication_to_request(
                    authentication_id=proxy.authentication_id,
                    request=request
                )
            await proxy.connect(timeout_seconds=self._timeout_seconds, buffer_size_bytes=self._buffer_size_bytes)
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
        self._log.debug(f'Tunneling data from {source} to {destination} finished')
