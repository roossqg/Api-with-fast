from pydantic import BaseModel, ConfigDict, EmailStr


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
