from pathlib import Path

import pytest

from proxy_server.domain.request import Request
from proxy_server.domain.request_method import RequestMethod
from routing.proxy_routing_not_found_exception import ProxyRoutingNotFoundException
from routing.request_hostname_pattern_proxy_router import RequestHostnamePatternProxyRouter


@pytest.fixture(scope='function')
def routing_config_file_path_mock(tmp_path: Path) -> Path:
    config_file_path: Path = tmp_path / 'routing.json'
    config_file_path.write_text(
        '[{"requestHostnamePattern": "*.test-domain.com", "proxyId": "test-proxy"}]'
    )
    return config_file_path


@pytest.fixture(scope='function')
def request_hostname_pattern_proxy_router(routing_config_file_path_mock: Path) -> RequestHostnamePatternProxyRouter:
    return RequestHostnamePatternProxyRouter(routing_config_file_path_mock)


@pytest.mark.asyncio
async def test_route_request_to_proxy(request_hostname_pattern_proxy_router: RequestHostnamePatternProxyRouter) -> None:
    request: Request = Request(
        method=RequestMethod.get,
        target='/',
        http_version='HTTP/1.1',
        hostname='example.test-domain.com'
    )
    proxy_id: str = await request_hostname_pattern_proxy_router.route_request_to_proxy(request)
    assert proxy_id == 'test-proxy'


@pytest.mark.asyncio
async def test_route_request_to_proxy_no_match(
    request_hostname_pattern_proxy_router: RequestHostnamePatternProxyRouter
) -> None:
    request: Request = Request(
        method=RequestMethod.get,
        target='/',
        http_version='HTTP/1.1',
        hostname='example.com'
    )
    with pytest.raises(ProxyRoutingNotFoundException):
        await request_hostname_pattern_proxy_router.route_request_to_proxy(request)
