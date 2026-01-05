from http import HTTPStatus

# client = TestClient(app)


def test_val(client):

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello'}


def test_post(client):

    response = client.post(
        '/users/',
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
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'username': 'carl', 'email': 'carl@example.com', 'id': 1}]
    }


def test_update_user(client):
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


def delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'user deleted'}
