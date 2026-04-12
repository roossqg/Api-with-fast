from http import HTTPStatus

from fast_pr.security import create_access_token


def test_val(client):

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello'}


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
