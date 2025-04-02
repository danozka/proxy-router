import asyncio
import logging
from logging import Logger

from proxy_router import ProxyRouter, RequestBasicAuthenticationAdder
from settings import Settings


log: Logger = logging.getLogger(__name__)


if __name__ == '__main__':
    try:
        settings: Settings = Settings()
        logging.basicConfig(
            format='%(asctime)s.%(msecs)03d - [%(levelname)s] - %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S',
            level=settings.logging_level
        )
        proxy: ProxyRouter = ProxyRouter(
            proxy_host=settings.proxy_host,
            proxy_port=settings.proxy_port,
            host=settings.host,
            port=settings.port,
            timeout_seconds=settings.timeout_seconds,
            buffer_size_bytes=settings.buffer_size_bytes,
            request_authentication_adder=RequestBasicAuthenticationAdder(
                user=settings.user,
                password=settings.password
            )
        )
        asyncio.run(proxy.start())
    except Exception as ex:
        log.error(f'Exception found while starting application: {ex.__class__.__name__}')
    finally:
        log.info('Application stopped')
        logging.shutdown()
