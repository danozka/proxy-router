import asyncio
import logging
from logging import Logger

from authentication import RequestBasicAuthenticationAdder
from my_company.my_company_proxy_getter import MyCompanyProxyGetter
from proxy_router import ProxyRouter
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
            proxy_getter=MyCompanyProxyGetter(),
            host=settings.proxy_router_host,
            port=settings.proxy_router_port,
            timeout_seconds=settings.proxy_router_timeout_seconds,
            buffer_size_bytes=settings.proxy_router_buffer_size_bytes,
            request_authentication_adder=RequestBasicAuthenticationAdder(
                user=settings.basic_auth_user,
                password=settings.basic_auth_password
            )
        )
        asyncio.run(proxy.start())
    except Exception as ex:
        log.error(f'Exception found while starting application: {ex.__class__.__name__}')
    finally:
        log.info('Application stopped')
        logging.shutdown()
