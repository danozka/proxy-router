class ProxyRoutingNotFoundException(Exception):
    def __init__(self, request_hostname: str) -> None:
        super().__init__(f'Proxy match not found for request hostname \'{request_hostname}\'')
