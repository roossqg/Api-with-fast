import factory.fuzzy
from fast_pr.models import Todo,Todostate

import pytest

#create todos data
class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    status= factory.fuzzy.FuzzyChoice(Todostate)


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


