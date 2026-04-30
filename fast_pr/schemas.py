from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fast_pr.models import Todostate


class Mens(BaseModel):
    message: str  # structure of an Data on App


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):  # -> no passaword view format in network
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
    # translate orm objects


class Userdb(UserSchema):
    id: int


class Userlist(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: Annotated[int, Field(0, ge=0)]
    limit: Annotated[int, Field(100, ge=1)]


# task
class TodoSchema(BaseModel):
    title: str
    description: str
    status: Todostate


# order-return
class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


# task list
class TodoList(BaseModel):
    todos: list[TodoPublic]


# order-filter
class FilterTodo(FilterPage):
    title: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=20)
    status: Todostate | None = None


# update todo
class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Todostate | None = None
