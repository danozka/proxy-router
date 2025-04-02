import logging
from logging import Logger

from proxy_router import IProxyGetter, Request, request_id_context
from proxy_router.proxy import Proxy


class MyCompanyProxyGetter(IProxyGetter):
    _log: Logger = logging.getLogger(__name__)

    def get_proxy(self, request: Request) -> Proxy:
        self._log.debug(f'[{request_id_context.get()}] Getting proxy...')
        return Proxy(host='127.0.0.1', port=3128)
