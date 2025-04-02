from dataclasses import dataclass


@dataclass
class Proxy:
    host: str
    port: int
