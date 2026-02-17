from http import HTTPStatus

from fastapi import FastAPI, HTTPException,Depends
from fastapi.responses import HTMLResponse

from fast_pr.schemas import Mens, Userdb, Userlist, UserPublic, UserSchema
from fast_pr.database import get_session
from fast_pr.models import Users

from sqlalchemy.orm import Session
from sqlalchemy import select

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
def create_user(user: UserSchema,session:Session=Depends(get_session)):
    #logs with session
    db_user = session.scalar(
        select(Users).where(
            (Users.name==user.username) | (Users.email==user.email)
        )
    )

    if db_user:
    #verify in databse

        if db_user.name == user.username:
            raise HTTPException(
                HTTPStatus.CONFLICT,
                detail="username already exists",
            )
        
        if db_user.email == user.email:
            raise HTTPException(
                HTTPStatus.CONFLICT,
                detail="email already exists",
            )
        

    db_user = Users(
        name = user.username,email = user.email,password = user.password
    )
        

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user

@app.get('/users/', response_model=Userlist)
def read_database():
    return {'users': user_database}


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
