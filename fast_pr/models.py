from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


class Todostate(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@mapped_as_dataclass(table_registry)  # get metadata with orm
class Users:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    creation: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    last_update: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    # user tasks
    todos: Mapped[list['Todo']] = relationship(
        init=False, cascade='all,delete-orphan', lazy='selectin'
    )

    # init : increment


@mapped_as_dataclass(table_registry)
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[Todostate]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped[Users] = relationship(init=False, back_populates='todos')

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    # use migrations to alter the orm table object
