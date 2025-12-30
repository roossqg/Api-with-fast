from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_pr.app import app


def val_test():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello11'}
