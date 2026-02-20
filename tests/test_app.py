from http import HTTPStatus

from fast_pr.schemas import UserPublic


def test_val(client):

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello'}


def test_post(client):

    response = client.post(
        '/users',
        json={
            'username': 'carl',
            'email': 'carl@example.com',
            'password': 'sdf',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'carl',
        'email': 'carl@example.com',
        'id': 1,
    }


def test_getusers(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_correct_getuser(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.json() == {'users': [user_schema]}


def test_update_user_ok(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'show',
            'email': 'show@example.com',
            'password': 'passaport',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'show',
        'email': 'show@example.com',
        'id': 1,
    }


def test_upd_integrity(client, user):

    client.post(
        '/users/',
        json={
            'username': 'jonson',
            'email': 'jonson@example.com',
            'password': 'jsd5'
        }
    )

    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'jonson',  # same username (conflic because is unique)
            'email': 'show@example.com',
            'password': 'passaport',
        }
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'username or email already exists'}


def test_get_user_ok(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'carl',
        'email': 'carl@example.com',
        'id': 1,
    }


def test_update_user_not(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'show',
            'email': 'show@example.com',
            'password': 'passaport',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'user not found'}


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'user deleted'}


def test_delete_user_not(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'user not found'}


def test_get_user_not(client):
    response = client.get('/users/1999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'no user here'}


# model reponse from exception

# all this in due order to use respecting database
