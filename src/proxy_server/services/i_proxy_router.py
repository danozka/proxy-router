from abc import ABC, abstractmethod

from proxy_server.domain.request import Request


class IProxyRouter(ABC):
    @abstractmethod
    async def route_request_to_proxy(self, request: Request) -> str:
        raise NotImplementedError
