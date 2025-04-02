from dataclasses import dataclass, field

from proxy_router.request_method import RequestMethod


@dataclass
class Request:
    method: RequestMethod
    path: str
    http_version: str
    headers: dict[str, str] = field(default_factory=dict, repr=False)
    body: str | None = field(default=None, repr=False)
    hostname: str | None = field(default=None, repr=False)
