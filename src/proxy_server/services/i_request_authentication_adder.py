from abc import ABC, abstractmethod

from proxy_server.domain.request import Request


class IRequestAuthenticationAdder(ABC):
    @abstractmethod
    async def add_authentication_to_request(self, authentication_id: str, request: Request) -> None:
        raise NotImplementedError
