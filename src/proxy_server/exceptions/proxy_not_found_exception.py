class ProxyNotFoundException(Exception):
    def __init__(self, proxy_id: str) -> None:
        super().__init__(f'Proxy with ID \'{proxy_id}\' not found')
