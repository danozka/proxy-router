import base64
from pathlib import Path

import pytest

from authentication.credentials_not_found_exception import CredentialsNotFoundException
from authentication.request_basic_authentication_adder import RequestBasicAuthenticationAdder
from proxy_server.domain.request import Request
from proxy_server.domain.request_method import RequestMethod


USERNAME: str = 'test-user'
PASSWORD: str = 'test-password'


@pytest.fixture(scope='function')
def auth_config_file_path_mock(tmp_path: Path) -> Path:
    config_file_path: Path = tmp_path / 'auth.json'
    config_file_path.write_text(
        f'[{{"id": "test-auth-id", "username": "{USERNAME}", "password": "{PASSWORD}"}}]'
    )
    return config_file_path


@pytest.fixture(scope='function')
def request_basic_authentication_adder(auth_config_file_path_mock: Path) -> RequestBasicAuthenticationAdder:
    return RequestBasicAuthenticationAdder(auth_config_file_path_mock)


@pytest.mark.asyncio
async def test_add_authentication_to_request(
    request_basic_authentication_adder: RequestBasicAuthenticationAdder
) -> None:
    request: Request = Request(
        method=RequestMethod.get,
        target='/',
        http_version='HTTP/1.1',
        hostname="test-domain.com"
    )
    await request_basic_authentication_adder.add_authentication_to_request(
        authentication_id='test-auth-id',
        request=request
    )
    expected_token = base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()
    assert request.headers.get('Proxy-Authorization') is not None
    assert request.headers.get('Proxy-Authorization') == f'Basic {expected_token}'


@pytest.mark.asyncio
async def test_add_authentication_to_request_credentials_not_found(
    request_basic_authentication_adder: RequestBasicAuthenticationAdder
) -> None:
    request: Request = Request(
        method=RequestMethod.get,
        target='/',
        http_version='HTTP/1.1',
        hostname="test.test-domain.com"
    )
    with pytest.raises(CredentialsNotFoundException):
        await request_basic_authentication_adder.add_authentication_to_request(
            authentication_id='non-existing-auth-id',
            request=request
        )
