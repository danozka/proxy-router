from contextvars import ContextVar
from uuid import UUID


request_id_context: ContextVar[UUID] = ContextVar('request_id')
