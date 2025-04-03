from abc import ABC, abstractmethod

from proxy_server.proxy import Proxy
from proxy_server.request import Request


class IProxyRouter(ABC):
    @abstractmethod
    async def route_request_to_proxy(self, request: Request) -> Proxy:
        raise NotImplementedError
