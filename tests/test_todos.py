from http import HTTPStatus

import factory.fuzzy
import pytest
from sqlalchemy import select

from fast_pr.models import Todo, Todostate, Users


# create todos data
class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    status = factory.fuzzy.FuzzyChoice(Todostate)


def test_create_todos(client, token, mock_db):
    # access db to alter time
    with mock_db(model=Todo) as time:
        response = client.post(
            '/to-do/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'test Todo title',
                'description': 'test Todo Desc',
                'status': 'draft',
            },
        )

    # return,user public and schema
    assert response.json() == {
        'id': 1,
        'title': 'test Todo title',
        'description': 'test Todo Desc',
        'status': 'draft',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_return_all(client, user, session, token):
    expected_todos = 5
    # create todo with 5 atributes with user id
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        '/to-do/',
        headers={'Authorization': f'Bearer {token}'},
    )

    # todos orm object
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_pagination_todos(client, user, session, token):
    expected_todos = 3
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        '/to-do/?offset=1&limit=3',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title(client, user, token, session):
    expected_todos = 5

    # direct in db
    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, title='Test Todolist title'
        ),
    )

    await session.commit()

    # search per title
    response = client.get(
        '/to-do/?title=Test Todolist title',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_big_title(token, client):
    big_t = 's' * 21

    response = client.get(
        f'/to-do/?title={big_t}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_small_title(token, client):
    small_t = 's'

    response = client.get(
        f'/to-do/?title={small_t}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_small_description(token, client):
    small_d = 'a'

    response = client.get(
        f'/to-do/?description={small_d}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_big_description(token, client):
    big_d = 's' * 21

    response = client.get(
        f'/to-do/?title={big_d}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_todos_filter_description(client, user, session, token):

    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, description='Test Todolist Desc'
        )
    )

    await session.commit()

    response = client.get(
        '/to-do/?description=Test Todolist Desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_status(client, user, session, token):

    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, status=Todostate.draft)
    )

    await session.commit()

    response = client.get(
        '/to-do/?status=draft', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_all_features(
    client, user, session, token, mock_db
):

    # access db
    with mock_db(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)

        # proccess
        session.add(todo)
        await session.commit()

    # get users
    await session.refresh(todo)

    response = client.get(
        '/to-do/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
            'id': todo.id,
            'description': todo.description,
            'title': todo.title,
            'status': todo.status,
        }
    ]


# ---update task
@pytest.mark.asyncio
async def test_todo_patch(user, session, token, client):
    todo = TodoFactory(user_id=user.id)

    # add on db for test
    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/to-do/{todo.id}',
        json={'title': 'test upd'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'test upd'


def test_todo_patch_error(user, session, token, client):
    response = client.patch(
        '/to-do/22',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_todo_delete(user, token, session, client):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/to-do/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task full Deleted'}


def test_todo_delete_error(token, client):
    response = client.delete(
        f'/to-do/{444}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'todo not found'}


# ---task format
@pytest.mark.asyncio
async def test_todos_all_fields(user, client, session, token, mock_db):
    # creating user in db
    with mock_db(model=Todo) as time:
        todo = TodoFactory(user_id=user.id)

        session.add(todo)
        await session.commit()

    # await for access that user
    await session.refresh(todo)

    response = client.get(
        '/to-do/',
        headers={'Authorization': f'Bearer {token}'},
    )
    # fields of user:
    assert response.json()['todos'] == [
        {
            'title': todo.title,
            'description': todo.description,
            'status': todo.status,
            'id': todo.id,
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
        }
    ]


@pytest.mark.asyncio
async def test_lookup(session, user: Users):
    todo = Todo(
        title='test todo',
        description='test todo desc',
        status='nothing',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    # not refresh because is not allowed

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))
