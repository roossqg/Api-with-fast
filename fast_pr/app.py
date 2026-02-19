from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_pr.database import get_session
from fast_pr.models import Users
from fast_pr.schemas import Mens, Userdb, Userlist, UserPublic, UserSchema

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

    # define user and insert into db:
    db_user = Users(
        username=user.username, email=user.email, password=user.password
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
def update_user(user_id: int, user: UserSchema):  # user for modify

    if user_id > len(user_database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    user_with_id = Userdb(**user.model_dump(), id=user_id)
    user_database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=Mens)
def delete_users(user_id: int):
    if user_id > len(user_database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    del user_database[user_id - 1]

    return {'message': 'user deleted'}


# just one method.tests are the server comunnications (2xx,4xx,etc)
@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int):
    if user_id > len(user_database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='no user here'
        )

    return user_database[user_id - 1]


# index is not database id
