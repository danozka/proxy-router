import logging
from fnmatch import fnmatch
from logging import Logger
from pathlib import Path

from aiopath import AsyncPath
from pydantic import TypeAdapter

from proxy_server import IProxyRouter, Request
from routing.proxy_routing_not_found_exception import ProxyRoutingNotFoundException
from routing.request_hostname_pattern_proxy_routing import RequestHostnamePatternProxyRouting


class RequestHostnamePatternProxyRouter(IProxyRouter):
    _log: Logger = logging.getLogger(__name__)
    _routing_config_file_path: AsyncPath

    def __init__(self, routing_config_file_path: Path) -> None:
        self._routing_config_file_path = AsyncPath(routing_config_file_path)

    async def route_request_to_proxy(self, request: Request) -> str:
        self._log.debug(f'Getting proxy for hostname \'{request.hostname}\'...')
        async with self._routing_config_file_path.open(mode='r') as file:
            routing_list: list[RequestHostnamePatternProxyRouting] = TypeAdapter(
                list[RequestHostnamePatternProxyRouting]
            ).validate_json(await file.read())
        routing: RequestHostnamePatternProxyRouting
        for routing in routing_list:
            if fnmatch(name=request.hostname, pat=routing.request_hostname_pattern):
                result: str = routing.proxy_id
                self._log.debug(f'Proxy for hostname \'{request.hostname}\' retrieved')
                return result
        raise ProxyRoutingNotFoundException(request.hostname)
