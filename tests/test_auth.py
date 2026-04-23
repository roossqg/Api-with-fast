from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expired_after_time(client, user):
    with freeze_time('2026-01-02 00:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

        with freeze_time('2026-01-02 00:41:00'):
            response = client.put(
                f'/users/{user.id}',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'username': 'zaxi',
                    'email': 'zaxi@example.com',
                    'password': 'zxx23',
                },
            )

            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert response.json() == {
                'detail': 'could not validate credentials'
            }
