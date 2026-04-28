from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_pr.database import get_session
from fast_pr.models import Todo, Users
from fast_pr.schemas import (
    FilterTodo,
    Mens,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_pr.security import get_current_user

router = APIRouter(prefix='/to-do', tags=['to-do'])

SessionB = Annotated[AsyncSession, Depends(get_session)]
CurrentUserB = Annotated[Users, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
async def create_todo_(
    todo: TodoSchema,
    user: CurrentUserB,
    session: SessionB,
):

    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        status=todo.status,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
async def list_todos(
    session: SessionB,
    user: CurrentUserB,
    todo_filter: Annotated[FilterTodo, Query()],
):

    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.status:
        query = query.filter(Todo.status == todo_filter.status)

    # acess db with filters
    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos': todos.all()}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def update_todo(
    session: SessionB, user: CurrentUserB, todo: TodoUpdate, todo_id: int
):

    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    # setting changes  #change model
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Mens)
async def todo_delete(user: CurrentUserB, session: SessionB, todo_id: int):

    # acess todo for del:
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='todo not found'
        )

    # del
    await session.delete(todo)
    await session.commit()

    return {'message': 'Task full Deleted'}
