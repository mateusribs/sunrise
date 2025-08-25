from pwdlib import PasswordHash


class PasswordService:
    """Implementação do serviço de senha usando bcrypt"""

    def __init__(self):
        self._pwd_context = PasswordHash.recommended()

    def hash_password(self, password: str) -> str:
        """Gera hash da senha usando bcrypt"""
        return self._pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha confere com o hash"""
        return self._pwd_context.verify(password, hashed)
