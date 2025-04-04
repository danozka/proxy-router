import base64
import logging
from logging import Logger
from pathlib import Path

from aiopath import AsyncPath
from pydantic import TypeAdapter

from authentication.basic_authentication_credentials import BasicAuthenticationCredentials
from authentication.credentials_not_found_exception import CredentialsNotFoundException
from proxy_server import IRequestAuthenticationAdder, Request


class RequestBasicAuthenticationAdder(IRequestAuthenticationAdder):
    _log: Logger = logging.getLogger(__name__)
    _auth_config_file_path: AsyncPath

    def __init__(self, auth_config_file_path: Path) -> None:
        self._auth_config_file_path = AsyncPath(auth_config_file_path)

    async def add_authentication_to_request(self, authentication_id: str, request: Request) -> None:
        self._log.debug('Adding basic authentication headers...')
        async with self._auth_config_file_path.open(mode='r') as file:
            credentials: list[BasicAuthenticationCredentials] = TypeAdapter(
                list[BasicAuthenticationCredentials]
            ).validate_json(await file.read())
        proxy_credentials: BasicAuthenticationCredentials | None = next(
            (x for x in credentials if x.id == authentication_id),
            None
        )
        if proxy_credentials is None:
            raise CredentialsNotFoundException(authentication_id)
        encoded_credentials: str = (
            base64.b64encode(f'{proxy_credentials.username}:{proxy_credentials.password}'.encode()).decode()
        )
        request.headers['Proxy-Authorization'] = f'Basic {encoded_credentials}'
        self._log.debug('Basic authentication headers added')
