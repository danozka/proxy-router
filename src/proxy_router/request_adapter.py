from urllib.parse import ParseResult, urlparse

from proxy_router.request import Request
from proxy_router.request_method import RequestMethod


class RequestAdapter:
    @staticmethod
    def adapt_request_from_bytes(request: bytes) -> Request | None:
        if not request:
            return None

        lines: list[str] = request.decode().splitlines()
        start_line: list[str] = lines[0].split()
        method: str = start_line[0]
        path: str = start_line[1]
        http_version: str = start_line[2]

        headers: dict[str, str] = {}
        body: str | None = None
        in_headers: bool = True
        line: str
        for line in lines[1:]:
            if in_headers:
                if line == '':
                    in_headers = False
                else:
                    key: str
                    value: str
                    key, value = line.split(sep=':', maxsplit=1)
                    headers[key.strip()] = value.strip()
            else:
                body = line if body is None else body + line + '\n'

        hostname: str | None
        if 'Host' not in headers:
            parsed_url: ParseResult = urlparse(path)
            hostname = parsed_url.hostname
        else:
            hostname = headers['Host']
        if hostname is not None:
            if ':' in hostname:
                hostname = hostname.split(':')[0]

        return Request(
            method=RequestMethod(method),
            path=path,
            http_version=http_version,
            headers=headers,
            body=body,
            hostname=hostname
        )

    @staticmethod
    def adapt_request_to_bytes(request: Request) -> bytes:
        request_string: str = f'{request.method.value} {request.path} {request.http_version}\r\n'
        request_string += '\r\n'.join([f'{key}: {value}' for key, value in request.headers.items()]) + '\r\n\r\n'
        if request.body is not None:
            request_string += request.body
        return request_string.encode()
