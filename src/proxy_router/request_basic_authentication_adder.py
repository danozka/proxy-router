import base64
import logging
from logging import Logger

from proxy_router.i_request_authentication_adder import IRequestAuthenticationAdder
from proxy_router.request import Request
from proxy_router.request_context import request_id_context


class RequestBasicAuthenticationAdder(IRequestAuthenticationAdder):
    _log: Logger = logging.getLogger(__name__)
    _encoded_credentials: str

    def __init__(self, user: str, password: str) -> None:
        self._encoded_credentials = base64.b64encode(f'{user}:{password}'.encode()).decode()

    def add_authentication_to_request(self, request: Request):
        self._log.debug(f'[{request_id_context.get()}] Adding basic authentication headers...')
        request.headers['Proxy-Authorization'] = f'Basic {self._encoded_credentials}'
