from abc import ABC, abstractmethod

from proxy_router.request import Request


class IRequestAuthenticationAdder(ABC):
    @abstractmethod
    def add_authentication_to_request(self, request: Request) -> None:
        raise NotImplementedError
