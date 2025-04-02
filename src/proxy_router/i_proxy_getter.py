from abc import ABC, abstractmethod

from proxy_router.proxy import Proxy
from proxy_router.request import Request


class IProxyGetter(ABC):
    @abstractmethod
    def get_proxy(self, request: Request) -> Proxy:
        raise NotImplementedError
