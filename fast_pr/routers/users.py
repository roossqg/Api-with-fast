from fastapi import APIRouter


from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException,Query
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from typing import Annotated


from fast_pr.database import get_session
from fast_pr.models import Users
from fast_pr.schemas import Mens, Token, Userlist, UserPublic, UserSchema, Filterpage
from fast_pr.security import (
    create_access_token,
    get_current_user,
    get_hash_password,
    verify_password,
)


#use this app on users endpoints.this works on application funcionality
router = APIRouter(prefix='/users',tags=['users'])

Session = Annotated[Session,Depends(get_session)]
Current_user = Annotated[Users,Depends(get_current_user)]




@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)

def create_user(user: UserSchema, session : Session):

    # logs with session
    db_user = session.scalar(
        select(Users).where(
            (Users.username == user.username) | (Users.email == user.email)
        )
    )  # verify if found user is already in db:

    if db_user:
        # verify in databse

        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='username already exists',
            )

        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='email already exists',
            )

    hashed_password = get_hash_password(user.password)

    # define user and insert into db:
    db_user = Users(
        username=user.username, email=user.email, password=hashed_password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user



