from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode
from pwdlib import PasswordHash

SECRET_KEY = 'nothing'
ALGORITHM = 'HS256'

ACESSS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = PasswordHash.recommended()
# transform hash


def create_acess_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACESSS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_hash_password(password: str):
    """stores password in hash for login later"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """login and compares with hashed password"""
    return pwd_context.verify(plain_password, hashed_password)
