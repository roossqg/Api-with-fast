from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_pr.database import get_session
from fast_pr.models import Users
from fast_pr.settings import Settings



SECRET_KEY = Settings.SECRET_KEY
ALGORITHM = Settings.ALGORITHM
ACESSS_TOKEN_EXPIRE_MINUTES = Settings.ACESSS_TOKEN_EXPIRE_MINUTES

pwd_context = PasswordHash.recommended()
# transform hash


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACESSS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})
    encoded_jwt = encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )

    return encoded_jwt


def get_hash_password(password: str):
    """stores password in hash for login later"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """login and compares with hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='auth/token', refreshUrl='auth/refresh'
)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token, SECRET_KEY, algorithms=ALGORITHM
        )
        subject_email = payload.get('sub')

        if not subject_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception

    user = await session.scalar(
        select(Users).where(Users.email == subject_email)
    )

    if not user:
        raise credentials_exception

    return user
