from http import HTTPStatus

from fast_pr.schemas import UserPublic
from fast_pr.security import create_access_token


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


def test_post_not_name(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'carl@example.com',
            'password': 'sdf',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username already exists'}


def test_post_not_email(client, user):
    response = client.post(
        '/users/',
        json={'username': 'carl', 'email': user.email, 'password': 'sdf'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'email already exists'}


def test_getusers(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_correct_getuser(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.json() == {'users': [user_schema]}


def test_update_user_ok(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
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
        'id': user.id,
    }


def test_delete_user(client, user, token):

    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'user deleted'}


def test_upd_integrity_put_post(client, user, other_user, token):

    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            # same username (conflic because is unique)
            'email': 'show@example.com',
            'password': 'passaport',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'username or email already exists'
    }


def test_get_user_not(client):
    response = client.get('/users/1999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'no user here'}


def test_get_user_ok(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


# model reponse from exception

# all this in due order to use respecting databas


def test_current_user_not_found_email(client):
    data = {'no-email': 'test'}  # no email to auth
    token = create_access_token(data)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}


def test_current_user_not_found(client):
    data = {'sub': 'test@www'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}


def test_update_user_wrong_data(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'zani',
            'email': 'zani@example.com',
            'password': 'zx12',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not Enough Permissions'}


def test_deleter_wrong_data(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not Enough Permissions'}
