from dataclasses import dataclass


@dataclass
class Request:
    start_line: str
    headers: dict[str, str]

    def is_https(self) -> bool:
        return self.start_line.startswith('CONNECT')
