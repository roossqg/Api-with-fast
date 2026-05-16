import os
from http import HTTPStatus

from jwt import decode

from fast_pr.security import create_access_token


def test_jwt():
    """create a fictional token and send to security endpoint"""
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, os.getenv('SECRET_KEY'), algorithms=os.getenv('ALGORITHM')
    )

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid(client):
    response = client.delete(
        '/users/9998', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}
