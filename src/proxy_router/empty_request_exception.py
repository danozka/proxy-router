class EmptyRequestException(Exception):
    def __init__(self) -> None:
        super().__init__('Request without content')
