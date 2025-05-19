from asyncio import Server, StreamReader, StreamWriter
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import TypeAdapter

from proxy_server.domain.proxy import Proxy
from proxy_server.domain.request import Request
from proxy_server.domain.request_method import RequestMethod
from proxy_server.request_adapter import RequestAdapter
from proxy_server.services.i_proxy_router import IProxyRouter
from proxy_server.services.i_request_authentication_adder import IRequestAuthenticationAdder
from proxy_server.proxy_server import ProxyServer


HOST: str = '0.0.0.0'
PORT: int = 8888
TIMEOUT_SECONDS: float = 60.0
BUFFER_SIZE_BYTES: int = 4096


@pytest.fixture(scope='function')
def proxy_config_file_path_mock(tmp_path: Path) -> Path:
    config_file_path: Path = tmp_path / 'proxy.json'
    config_file_path.write_text(
        '[{"id": "test-proxy", "hostname": "test.test-domain.com", "port": 80, "authenticationId": "test-user"}]'
    )
    return config_file_path


@pytest.fixture(scope='function')
def proxy_mock() -> AsyncMock:
    proxy: AsyncMock = AsyncMock(spec=Proxy)
    proxy.id = 'test-proxy'
    proxy.authentication_id = 'test-user'
    return proxy


@pytest.fixture(scope='function')
def proxy_router_mock() -> AsyncMock:
    proxy_router: AsyncMock = AsyncMock(spec=IProxyRouter)
    proxy_router.route_request_to_proxy.return_value = 'test-proxy'
    return proxy_router


@pytest.fixture(scope='function')
def request_adapter_mock() -> Mock:
    return Mock(spec=RequestAdapter)


@pytest.fixture(scope='function')
def request_authentication_adder_mock() -> AsyncMock:
    return AsyncMock(spec=IRequestAuthenticationAdder)


@pytest.fixture(scope='function')
def client_reader_mock() -> AsyncMock:
    return AsyncMock(spec=StreamReader)


@pytest.fixture(scope='function')
def client_writer_mock() -> AsyncMock:
    return AsyncMock(spec=StreamWriter)


@pytest.mark.asyncio
async def test_start(
    proxy_config_file_path_mock: Path,
    proxy_router_mock: AsyncMock,
    request_adapter_mock: Mock
) -> None:
    proxy_server: ProxyServer = ProxyServer(
        proxy_config_file_path=proxy_config_file_path_mock,
        proxy_router=proxy_router_mock,
        host=HOST,
        port=PORT,
        request_adapter=request_adapter_mock
    )
    asyncio_start_server_mock: AsyncMock
    with patch('asyncio.start_server') as asyncio_start_server_mock:
        server_mock: AsyncMock = AsyncMock(spec=Server)
        asyncio_start_server_mock.return_value = server_mock
        await proxy_server.start()
        asyncio_start_server_mock.assert_awaited_once_with(
            client_connected_cb=proxy_server.handle_request,
            host=HOST,
            port=PORT
        )
        server_mock.serve_forever.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_request_http(
    proxy_config_file_path_mock: Path,
    proxy_mock: AsyncMock,
    proxy_router_mock: AsyncMock,
    request_adapter_mock: Mock,
    request_authentication_adder_mock: AsyncMock,
    client_reader_mock: AsyncMock,
    client_writer_mock: AsyncMock
) -> None:
    request_bytes: bytes = (
        b'POST /submit HTTP/1.1\r\n'
        b'Host: content.test-domain.com\r\n'
        b'Content-Type: application/json\r\n'
        b'Content-Length: 18\r\n'
        b'\r\n'
        b'{"key": "value"}'
    )
    request: Request = Request(
        method=RequestMethod.post,
        target='/submit',
        http_version='HTTP/1.1',
        headers={
            'Host': 'content.test-domain.com',
            'Content-Type': 'application/json',
            'Content-Length': '16'
        },
        body='{"key": "value"}',
        hostname='content.test-domain.com'
    )
    response_bytes: bytes = (
        b'HTTP/1.1 200 OK\r\n'
        b'Content-Type: text/plain\r\n'
        b'Content-Length: 31'
        b'\r\n'
        b'Message submitted successfully.'
    )
    proxy_mock.read.side_effect = [response_bytes, b'']
    proxy_router_mock.route_request_to_proxy.return_value = 'test-proxy'
    request_adapter_mock.adapt_request_from_bytes.return_value = request
    request_adapter_mock.adapt_request_to_bytes.return_value = request_bytes
    client_reader_mock.read.return_value = request_bytes
    proxy_server: ProxyServer = ProxyServer(
        proxy_config_file_path=proxy_config_file_path_mock,
        proxy_router=proxy_router_mock,
        timeout_seconds=TIMEOUT_SECONDS,
        buffer_size_bytes=BUFFER_SIZE_BYTES,
        request_adapter=request_adapter_mock,
        request_authentication_adder=request_authentication_adder_mock
    )
    with patch.object(target=TypeAdapter, attribute=TypeAdapter.validate_json.__name__, return_value=[proxy_mock]):
        await proxy_server.handle_request(client_reader=client_reader_mock, client_writer=client_writer_mock)
        proxy_mock.connect.assert_awaited_once_with(
            timeout_seconds=TIMEOUT_SECONDS,
            buffer_size_bytes=BUFFER_SIZE_BYTES
        )
        proxy_mock.write.assert_awaited_once_with(request_bytes)
        assert proxy_mock.read.await_count == 2
        proxy_mock.close.assert_awaited_once()
        proxy_router_mock.route_request_to_proxy.assert_awaited_once_with(request)
        request_adapter_mock.adapt_request_from_bytes.assert_called_once_with(request_bytes)
        request_adapter_mock.adapt_request_to_bytes.assert_called_once_with(request)
        request_authentication_adder_mock.add_authentication_to_request.assert_awaited_once_with(
            authentication_id=proxy_mock.authentication_id,
            request=request
        )
        client_reader_mock.read.assert_awaited_once_with(BUFFER_SIZE_BYTES)
        client_writer_mock.write.assert_called_once_with(response_bytes)
        client_writer_mock.drain.assert_awaited_once()
        client_writer_mock.close.assert_called_once()
        client_writer_mock.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_request_https(
    proxy_config_file_path_mock: Path,
    proxy_mock: AsyncMock,
    proxy_router_mock: AsyncMock,
    request_adapter_mock: Mock,
    request_authentication_adder_mock: AsyncMock,
    client_reader_mock: AsyncMock,
    client_writer_mock: AsyncMock
) -> None:
    request_bytes_connect: bytes = (
        b'CONNECT web.test-domain.com:443 HTTP/1.1\r\n'
        b'Host: web.test-domain.com:443\r\n'
        b'\r\n'
    )
    request_connect: Request = Request(
        method=RequestMethod.connect,
        target='web.test-domain.com:443',
        http_version='HTTP/1.1',
        headers={
            'Host': 'web.test-domain.com:443'
        },
        hostname='web.test-domain.com'
    )
    proxy_mock.read.side_effect = [
        (
            b'HTTP/1.1 200 Connection Established\r\n'
            b'\r\n'
        ),
        (
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/html\r\n'
            b'\r\n'
            b'<!DOCTYPE html><html>\r\n'
            b'<html><body><p>Hello world!</p></body></html>'
        ),
        b''
    ]
    proxy_router_mock.route_request_to_proxy.return_value = 'test-proxy'
    request_adapter_mock.adapt_request_from_bytes.return_value = request_connect
    request_adapter_mock.adapt_request_to_bytes.return_value = request_bytes_connect
    client_reader_mock.read.side_effect = [
        request_bytes_connect,
        (
            b'GET / HTTP/1.1\r\n'
            b'Host: web.test-domain.com\r\n'
            b'Accept: */*\r\n'
            b'\r\n'
        ),
        b''
    ]
    proxy_server: ProxyServer = ProxyServer(
        proxy_config_file_path=proxy_config_file_path_mock,
        proxy_router=proxy_router_mock,
        timeout_seconds=TIMEOUT_SECONDS,
        buffer_size_bytes=BUFFER_SIZE_BYTES,
        request_adapter=request_adapter_mock,
        request_authentication_adder=request_authentication_adder_mock
    )
    with patch.object(target=TypeAdapter, attribute=TypeAdapter.validate_json.__name__, return_value=[proxy_mock]):
        await proxy_server.handle_request(client_reader=client_reader_mock, client_writer=client_writer_mock)
        proxy_mock.connect.assert_awaited_once_with(
            timeout_seconds=TIMEOUT_SECONDS,
            buffer_size_bytes=BUFFER_SIZE_BYTES
        )
        assert proxy_mock.read.await_count == 3
        assert proxy_mock.write.await_count == 2
        proxy_mock.close.assert_awaited_once()
        proxy_router_mock.route_request_to_proxy.assert_awaited_once_with(request_connect)
        request_adapter_mock.adapt_request_from_bytes.assert_called_once_with(request_bytes_connect)
        request_adapter_mock.adapt_request_to_bytes.assert_called_once_with(request_connect)
        request_authentication_adder_mock.add_authentication_to_request.assert_awaited_once_with(
            authentication_id=proxy_mock.authentication_id,
            request=request_connect
        )
        client_reader_mock.read.assert_awaited_with(BUFFER_SIZE_BYTES)
        assert client_reader_mock.read.await_count == 3
        assert client_writer_mock.write.call_count == 2
        assert client_writer_mock.drain.await_count == 2
        client_writer_mock.close.assert_called_once()
        client_writer_mock.wait_closed.assert_awaited_once()



@pytest.mark.asyncio
async def test_handle_request_empty_request(
    proxy_config_file_path_mock: Path,
    proxy_router_mock: AsyncMock,
    request_adapter_mock: Mock,
    client_reader_mock: AsyncMock,
    client_writer_mock: AsyncMock
) -> None:
    request_adapter_mock.adapt_request_from_bytes.return_value = None
    proxy_server: ProxyServer = ProxyServer(
        proxy_config_file_path=proxy_config_file_path_mock,
        proxy_router=proxy_router_mock,
        buffer_size_bytes=BUFFER_SIZE_BYTES,
        request_adapter=request_adapter_mock
    )
    await proxy_server.handle_request(client_reader=client_reader_mock, client_writer=client_writer_mock)
    proxy_router_mock.route_request_to_proxy.assert_not_awaited()
    request_adapter_mock.adapt_request_from_bytes.assert_called_once()
    request_adapter_mock.adapt_request_to_bytes.assert_not_called()
    client_reader_mock.read.assert_awaited_once_with(BUFFER_SIZE_BYTES)
    client_writer_mock.write.assert_not_called()
    client_writer_mock.drain.assert_not_awaited()
    client_writer_mock.close.assert_called_once()
    client_writer_mock.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_request_proxy_not_found(
    proxy_config_file_path_mock: Path,
    proxy_router_mock: AsyncMock,
    request_adapter_mock: Mock,
    client_reader_mock: AsyncMock,
    client_writer_mock: AsyncMock
) -> None:
    request_bytes: bytes = (
        b'GET / HTTP/1.1\r\n'
        b'Host: map.test-domain.com\r\n'
        b'Accept: */*\r\n'
        b'\r\n'
    )
    request: Request = Request(
        method=RequestMethod.get,
        target='/',
        http_version='HTTP/1.1',
        headers={
            'Host': 'map.test-domain.com',
            'Accept': '*/*'
        },
        hostname='map.test-domain.com'
    )
    proxy_router_mock.route_request_to_proxy.return_value = 'test-proxy'
    request_adapter_mock.adapt_request_from_bytes.return_value = request
    client_reader_mock.read.return_value = request_bytes
    proxy_server: ProxyServer = ProxyServer(
        proxy_config_file_path=proxy_config_file_path_mock,
        proxy_router=proxy_router_mock,
        timeout_seconds=TIMEOUT_SECONDS,
        buffer_size_bytes=BUFFER_SIZE_BYTES,
        request_adapter=request_adapter_mock
    )
    with patch.object(target=TypeAdapter, attribute=TypeAdapter.validate_json.__name__, return_value=[]):
        await proxy_server.handle_request(client_reader=client_reader_mock, client_writer=client_writer_mock)
        proxy_router_mock.route_request_to_proxy.assert_awaited_once_with(request)
        request_adapter_mock.adapt_request_from_bytes.assert_called_once_with(request_bytes)
        request_adapter_mock.adapt_request_to_bytes.assert_not_called()
        client_reader_mock.read.assert_awaited_once_with(BUFFER_SIZE_BYTES)
        client_writer_mock.write.assert_not_called()
        client_writer_mock.drain.assert_not_awaited()
        client_writer_mock.close.assert_called_once()
        client_writer_mock.wait_closed.assert_awaited_once()
