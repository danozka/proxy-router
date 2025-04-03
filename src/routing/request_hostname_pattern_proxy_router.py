import logging
from fnmatch import fnmatch
from logging import Logger
from pathlib import Path

from aiopath import AsyncPath
from pydantic import TypeAdapter

from proxy_server import IProxyRouter, Request, request_id_context
from proxy_server.proxy import Proxy
from routing.proxy_match_not_found_exception import ProxyMatchNotFoundException
from routing.request_hostname_pattern_proxy_routing import RequestHostnamePatternProxyRouting


class RequestHostnamePatternProxyRouter(IProxyRouter):
    _log: Logger = logging.getLogger(__name__)
    _routing_config_file_path: AsyncPath
    _timeout_seconds: float
    _buffer_size_bytes: int

    def __init__(
        self,
        routing_config_file_path: Path,
        timeout_seconds: float = 2.0,
        buffer_size_bytes: int = 4096
    ) -> None:
        self._routing_config_file_path = AsyncPath(routing_config_file_path)
        self._timeout_seconds = timeout_seconds
        self._buffer_size_bytes = buffer_size_bytes

    async def route_request_to_proxy(self, request: Request) -> Proxy:
        self._log.debug(f'[{request_id_context.get()}] Getting proxy for hostname \'{request.hostname}\'...')
        async with self._routing_config_file_path.open(mode='r') as file:
            routing_list: list[RequestHostnamePatternProxyRouting] = TypeAdapter(
                list[RequestHostnamePatternProxyRouting]
            ).validate_json(await file.read())
        routing: RequestHostnamePatternProxyRouting
        for routing in routing_list:
            if fnmatch(name=request.hostname, pat=routing.request_hostname_pattern):
                result: Proxy = Proxy(
                    host=routing.proxy_host,
                    port=routing.proxy_port,
                    timeout_seconds=self._timeout_seconds,
                    buffer_size_bytes=self._buffer_size_bytes
                )
                self._log.debug(f'[{request_id_context.get()}] Proxy for hostname \'{request.hostname}\' retrieved')
                return result
        raise ProxyMatchNotFoundException(request.hostname)
