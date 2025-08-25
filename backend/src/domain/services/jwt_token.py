from datetime import datetime, timedelta
from typing import Any, Dict
from zoneinfo import ZoneInfo

from jwt import DecodeError, ExpiredSignatureError, decode, encode

from src.settings import Settings


class JWTTokenService:
    """Implementação do serviço de token usando JWT"""

    def __init__(self):
        self._access_token_expires_minutes = Settings().JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self._algorithm = Settings().JWT_ALGORITHM
        self._secret_key = Settings().JWT_SECRET_KEY

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Cria um token de acesso JWT"""
        to_encode = data.copy()
        expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
            minutes=self._access_token_expires_minutes
        )
        to_encode.update({'exp': expire})
        encoded_jwt = encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decodifica um token JWT e retorna os dados"""
        try:
            decoded = decode(token, self._secret_key, algorithms=[self._algorithm])
            return decoded

        except ExpiredSignatureError:
            raise ExpiredSignatureError('Token has expired')
        except DecodeError:
            raise DecodeError('Token is invalid')
        except Exception as e:
            raise Exception(f'An error occurred while decoding the token: {str(e)}')
