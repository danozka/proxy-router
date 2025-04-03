import base64
import logging
from logging import Logger

from proxy_server import IRequestAuthenticationAdder, Request


class RequestBasicAuthenticationAdder(IRequestAuthenticationAdder):
    _log: Logger = logging.getLogger(__name__)
    _encoded_credentials: str

    def __init__(self, user: str, password: str) -> None:
        self._encoded_credentials = base64.b64encode(f'{user}:{password}'.encode()).decode()

    def add_authentication_to_request(self, request: Request) -> None:
        self._log.debug('Adding basic authentication headers...')
        request.headers['Proxy-Authorization'] = f'Basic {self._encoded_credentials}'
        self._log.debug('Basic authentication headers added')
