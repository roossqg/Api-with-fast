from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
