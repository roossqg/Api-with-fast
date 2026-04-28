from http import HTTPStatus

import factory.fuzzy
import pytest

from fast_pr.models import Todo, Todostate


# create todos data
class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    status = factory.fuzzy.FuzzyChoice(Todostate)


def test_create_todos(client, token):
    response = client.post(
        '/to-do/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test Todo title',
            'description': 'test Todo Desc',
            'status': 'draft',
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'test Todo title',
        'description': 'test Todo Desc',
        'status': 'draft',
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

    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, title='Test Todolist title'
        ),
    )

    await session.commit()

    response = client.get(
        '/to-do/?title=Test Todolist title',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


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
async def test_list_todos_filter_all_features(client, user, session, token):

    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='all fields',
            description='all fields A',
            status=Todostate.draft,
        ),
    )

    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='other Tests all fields B',
            description='other Tests all fields A',
            status=Todostate.done,
        ),
    )

    await session.commit()

    response = client.get(
        '/to-do/?title=all fields&status=draft&description=all fields A',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


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


def test_todo_delete_error(user, token, session, client):
    response = client.delete(
        f'/to-do/{}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'todo not found'}


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
