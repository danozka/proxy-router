import pytest

from proxy_server.domain.request import Request
from proxy_server.domain.request_method import RequestMethod
from proxy_server.request_adapter import RequestAdapter


@pytest.fixture(scope='function')
def request_adapter() -> RequestAdapter:
    return RequestAdapter()


def test_adapt_request_from_bytes_with_none(request_adapter: RequestAdapter) -> None:
    assert request_adapter.adapt_request_from_bytes(None) is None


def test_adapt_request_from_bytes_with_valid_request_no_body(request_adapter: RequestAdapter) -> None:
    request_bytes: bytes = (
        b'GET /index.html HTTP/1.1\r\n'
        b'Host: example.com\r\n'
        b'User-Agent: test-agent\r\n'
        b'\r\n'
    )
    request: Request = request_adapter.adapt_request_from_bytes(request_bytes)
    assert request is not None
    assert request.method == RequestMethod.get
    assert request.target == '/index.html'
    assert request.http_version == 'HTTP/1.1'
    assert request.headers == {
        'Host': 'example.com',
        'User-Agent': 'test-agent'
    }
    assert request.body is None
    assert request.hostname == 'example.com'


def test_adapt_request_from_bytes_with_valid_request_with_body(request_adapter: RequestAdapter) -> None:
    request_bytes: bytes = (
        b'POST /submit HTTP/1.1\r\n'
        b'Host: api.example.com\r\n'
        b'Content-Type: application/json\r\n'
        b'Content-Length: 16\r\n'
        b'\r\n'
        b'{"key": "value"}'
    )
    request: Request = request_adapter.adapt_request_from_bytes(request_bytes)
    assert request is not None
    assert request.method == RequestMethod.post
    assert request.target == '/submit'
    assert request.http_version == 'HTTP/1.1'
    assert request.headers == {
        'Host': 'api.example.com',
        'Content-Type': 'application/json',
        'Content-Length': '16'
    }
    assert request.body == '{"key": "value"}'
    assert request.hostname == 'api.example.com'


def test_adapt_request_from_bytes_with_multiline_body(request_adapter: RequestAdapter) -> None:
    request_bytes: bytes = (
        b'POST /submit HTTP/1.1\r\n'
        b'Host: api.example.com\r\n'
        b'\r\n'
        b'line1\n'
        b'line2\n'
        b'line3'
    )
    request: Request = request_adapter.adapt_request_from_bytes(request_bytes)
    assert request is not None
    assert request.body == 'line1\nline2\nline3'


def test_adapt_request_from_bytes_with_host_in_headers(request_adapter: RequestAdapter) -> None:
    request_bytes: bytes = (
        b'GET /path HTTP/1.1\r\n'
        b'Host: header-host.com\r\n'
        b'\r\n'
    )
    request: Request = request_adapter.adapt_request_from_bytes(request_bytes)
    assert request.hostname == 'header-host.com'


def test_adapt_request_from_bytes_with_host_in_target(request_adapter: RequestAdapter) -> None:
    request_bytes: bytes = (
        b'GET http://target-host.com/path HTTP/1.1\r\n'
        b'\r\n'
    )
    request: Request = request_adapter.adapt_request_from_bytes(request_bytes)
    assert request.hostname == 'target-host.com'


def test_adapt_request_from_bytes_with_host_with_port(request_adapter: RequestAdapter) -> None:
    request_bytes: bytes = (
        b'GET /path HTTP/1.1\r\n'
        b'Host: host-with-port.com:8080\r\n'
        b'\r\n'
    )
    request: Request = request_adapter.adapt_request_from_bytes(request_bytes)
    assert request.hostname == 'host-with-port.com'


def test_adapt_request_to_bytes_with_no_body(request_adapter: RequestAdapter) -> None:
    request: Request = Request(
        method=RequestMethod.get,
        target='/index.html',
        http_version='HTTP/1.1',
        headers={
            'Host': 'example.com',
            'User-Agent': 'test-agent'
        },
        body=None,
        hostname='example.com'
    )
    expected_bytes: bytes = (
        b'GET /index.html HTTP/1.1\r\n'
        b'Host: example.com\r\n'
        b'User-Agent: test-agent\r\n'
        b'\r\n'
    )
    assert request_adapter.adapt_request_to_bytes(request) == expected_bytes


def test_adapt_request_to_bytes_with_body(request_adapter: RequestAdapter) -> None:
    request: Request = Request(
        method=RequestMethod.post,
        target='/submit',
        http_version='HTTP/1.1',
        headers={
            'Host': 'api.example.com',
            'Content-Type': 'application/json'
        },
        body='{"key": "value"}',
        hostname='api.example.com'
    )
    expected_bytes: bytes = (
        b'POST /submit HTTP/1.1\r\n'
        b'Host: api.example.com\r\n'
        b'Content-Type: application/json\r\n'
        b'\r\n'
        b'{"key": "value"}'
    )
    assert request_adapter.adapt_request_to_bytes(request) == expected_bytes


def test_adapt_request_to_bytes_with_empty_headers(request_adapter: RequestAdapter) -> None:
    request: Request = Request(
        method=RequestMethod.get,
        target='/',
        http_version='HTTP/1.1',
        headers={},
        body=None,
        hostname='example.com'
    )
    expected_bytes: bytes = b'GET / HTTP/1.1\r\n\r\n'
    assert request_adapter.adapt_request_to_bytes(request) == expected_bytes


def test_round_trip_conversion(request_adapter: RequestAdapter) -> None:
    original_bytes: bytes = (
        b'POST /api HTTP/1.1\r\n'
        b'Host: test.com\r\n'
        b'Content-Type: text/plain\r\n'
        b'\r\n'
        b'test body'
    )
    request: Request = request_adapter.adapt_request_from_bytes(original_bytes)
    converted_bytes: bytes = request_adapter.adapt_request_to_bytes(request)
    assert converted_bytes == original_bytes
