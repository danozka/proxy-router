from proxy_router.request import Request


class RequestAdapter:
    @staticmethod
    def adapt_request_from_bytes(request: bytes) -> Request | None:
        if not request:
            return None
        request_lines: list[str] = request.decode().splitlines()
        start_line: str = request_lines[0]
        headers: dict[str, str] = {}
        request_line: str
        for request_line in request_lines[1:]:
            if ':' in request_line:
                key: str
                value: str
                key, value = request_line.split(sep=':', maxsplit=1)
                headers[key.strip()] = value.strip()
            elif request_line == '':
                break
        return Request(start_line=start_line, headers=headers)

    @staticmethod
    def adapt_request_to_bytes(request: Request) -> bytes:
        request_lines: list[str] = [request.start_line] + [f'{key}: {value}' for key, value in request.headers.items()]
        return ('\r\n'.join(request_lines) + '\r\n\r\n').encode()
