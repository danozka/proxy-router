from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BasicAuthenticationCredentials(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    id: str
    username: str
    password: str

    def __str__(self) -> str:
        return self.__repr__()
