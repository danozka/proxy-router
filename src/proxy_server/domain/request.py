from dataclasses import dataclass, field

from proxy_server.domain.request_method import RequestMethod


@dataclass
class Request:
    method: RequestMethod
    target: str
    http_version: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = field(default=None, repr=False)
    hostname: str | None = field(default=None, repr=False)
