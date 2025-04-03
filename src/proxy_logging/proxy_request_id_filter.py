from logging import Filter, LogRecord
from uuid import UUID, uuid4

from proxy_server import request_id_context


class ProxyRequestIdFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        request_id: UUID = request_id_context.get() or uuid4()
        setattr(record, 'request', request_id)
        return True
