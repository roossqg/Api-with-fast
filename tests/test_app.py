from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_pr.app import app


def val_test():
    client = TestClient(app)

    response = client.get('/')
    response2 = client.get('/ht_res')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello11'}

    assert response2.status_code == HTTPStatus.OK
    assert '<h2>Hello world!!</h2>' in response2.text
