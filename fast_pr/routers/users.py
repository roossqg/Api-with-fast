from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_pr.database import get_session
from fast_pr.models import Users
from fast_pr.schemas import (
    Mens,
    Userlist,
    UserPublic,
    UserSchema,
)
from fast_pr.security import (
    get_current_user,
    get_hash_password,
)

# use this app on users endpoints.this works on application funcionality
router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session):

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


@router.get('/', response_model=Userlist)
def read_database(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(Users).offset(skip).limit(limit)).all()
    # orginal database

    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    # user for modify

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not Enough Permissions'
        )

    db_user = session.scalar(select(Users).where(Users.id == user_id))
    # search for one object on db

    if not db_user:  # not found
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    try:
        # apply changes on db user:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_hash_password(user.password)

        session.commit()  # no adds ,just modify atributes
        session.refresh(current_user)  # -> gets User public format to return

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already exists',
        )


@router.delete('/{user_id}', response_model=Mens)
def delete_users(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not Enough Permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'user deleted'}


@router.get('/{user_id`}', response_model=Mens)
def get_user(user_id: int, session: Session = Depends(get_session)):

    db_user = session.scalar(select(Users).where(Users.id == user_id))
    # model return

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='no user here'
        )

    # db_user = Users(
    # username=user.username, email=user.email, password=user.password

    return db_user
