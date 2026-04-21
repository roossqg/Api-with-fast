from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_pr.database import get_session
from fast_pr.models import Users
from fast_pr.schemas import FilterPage, Mens, Userlist, UserPublic, UserSchema
from fast_pr.security import (
    get_current_user,
    get_hash_password,
)

# use this app on users endpoints.this works on application funcionality
router = APIRouter(prefix='/users', tags=['users'])

SessionC = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[Users, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: SessionC):

    # logs with session
    db_user = await session.scalar(
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
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=Userlist)
async def read_database(
    session: SessionC, filter_users: Annotated[FilterPage, Query()]
):

    query = await session.scalars(
        select(Users).offset(filter_users.offset).limit(filter_users.limit)
    )

    users = query.all()
    # orginal database

    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionC,
    current_user: CurrentUser,
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

        await session.commit()  # no adds ,just modify atributes
        await session.refresh(current_user)
        # -> gets User public format to return

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already exists',
        )


@router.delete('/{user_id}', response_model=Mens)
async def delete_users(
    user_id: int,
    session: SessionC,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not Enough Permissions'
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'user deleted'}


@router.get('/{user_id}', response_model=UserPublic)
async def get_user(user_id: int, session: SessionC):

    db_user = await session.scalar(select(Users).where(Users.id == user_id))
    # model return

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='no user here'
        )

    # db_user = Users(
    # username=user.username, email=user.email, password=user.password

    return db_user
