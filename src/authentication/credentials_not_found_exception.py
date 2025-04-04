class CredentialsNotFoundException(Exception):
    def __init__(self, authentication_id: str) -> None:
        super().__init__(f'Credentials with ID \'{authentication_id}\' not found')
