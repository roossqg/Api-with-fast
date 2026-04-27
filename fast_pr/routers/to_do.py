from typing import Annotated

from fastapi import APIRouter, Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fast_pr.database import get_session
from fast_pr.models import Todo, Users
from fast_pr.schemas import TodoPublic, TodoSchema,TodoList,FilterTodo
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


@router.get('/',response_model=TodoList)
async def list_todos(
    session: SessionB,
    user: CurrentUserB,
    todo_filter: Annotated[FilterTodo,Query()]
):
    
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(
            Todo.title.contains(todo_filter))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter))

    if todo_filter.status:
        query = query.filter(Todo.status == todo_filter.status)


    #acess db with filters
    todos = await  session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos':todos.all()}