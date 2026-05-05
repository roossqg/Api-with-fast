from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_pr.models import Todo, Users


@pytest.mark.asyncio
async def test_create_user(session, mock_db):
    with mock_db(model=Users) as time:
        new_user = Users(
            username='Bob', password='as34ty', email='bob@example.com'
        )
        # send info to db
        session.add(new_user)

        await session.commit()

    user = await session.scalar(select(Users).where(Users.username == 'Bob'))
    # get and show data from db

    assert asdict(user) == {
        'id': 1,
        'username': 'Bob',
        'password': 'as34ty',
        'email': 'bob@example.com',
        'creation': time,
        'last_update': time,
        'todos': [],
    }

    # --> verify structure in db


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: Users):

    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        status='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(Users).where(Users.id == user.id))

    assert user.todos == [todo]
