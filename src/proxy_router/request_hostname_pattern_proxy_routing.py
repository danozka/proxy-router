from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RequestHostnamePatternProxyRouting(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    request_hostname_pattern: str
    proxy_host: str
    proxy_port: int

    def __str__(self) -> str:
        return self.__repr__()
