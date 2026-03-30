from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_pr.database import get_session
from fast_pr.models import Users
from fast_pr.schemas import Mens, Token, Userlist, UserPublic, UserSchema
from fast_pr.security import (
    create_acess_token,
    get_hash_password,
    verify_password,
)

app = FastAPI()
user_database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Mens)
def root():
    return {'message': 'hello'}


@app.get('/ht_res', response_class=HTMLResponse, status_code=200)
def hello1_htm():
    return """
    <html>
        <head>
            <title>page htm</title>
        </head>
        <body>
            <h2>Hello world!!</h2>
        </body>
    </html>
    """


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
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


@app.get('/users/', response_model=Userlist)
def read_database(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(Users).offset(skip).limit(limit)).all()
    # orginal database

    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    # user for modify

    db_user = session.scalar(select(Users).where(Users.id == user_id))
    # search for one object on db

    if not db_user:  # not found
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    try:
        # apply changes on db user:
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = get_hash_password(user.password)

        session.commit()  # no adds ,just modify atributes
        session.refresh(db_user)  # -> gets User public format to return

        return db_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already exists',
        )


@app.delete('/users/{user_id}', response_model=Mens)
def delete_users(user_id: int, session: Session = Depends(get_session)):

    db_user = session.scalar(select(Users).where(Users.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'user deleted'}


# just one method.tests are the server comunnications (2xx,4xx,etc)
@app.get('/users/{user_id}', response_model=UserPublic)
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


# index is not database id


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):

    user = session.scalar(
        select(Users).where(Users.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_acess_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
