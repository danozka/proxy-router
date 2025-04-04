import asyncio
import logging
from logging import Logger

from authentication import RequestBasicAuthenticationAdder
from proxy_logging import ProxyLoggingBuilder
from proxy_server import ProxyServer
from routing import RequestHostnamePatternProxyRouter
from settings import Settings


log: Logger = logging.getLogger(__name__)


if __name__ == '__main__':
    try:
        settings: Settings = Settings()
        proxy_logging_builder: ProxyLoggingBuilder = ProxyLoggingBuilder(settings.logging_level)
        proxy_logging_builder.build()
        proxy_server: ProxyServer = ProxyServer(
            proxy_config_file_path=settings.proxy_config_file_path,
            proxy_router=RequestHostnamePatternProxyRouter(settings.routing_config_file_path),
            host=settings.proxy_server_host,
            port=settings.proxy_server_port,
            timeout_seconds=settings.proxy_server_timeout_seconds,
            buffer_size_bytes=settings.proxy_server_buffer_size_bytes,
            request_authentication_adder=RequestBasicAuthenticationAdder(settings.authentication_config_file_path)
        )
        asyncio.run(proxy_server.start())
    except Exception as ex:
        log.error(f'Exception found while starting application: {ex.__class__.__name__} - {ex}')
    finally:
        log.info('Application stopped')
        logging.shutdown()
