from http import HTTPStatus


def test_read_root_deve_retornar_ok_e_ola_mundo(client):  # arrange
    response = client.get('/')  # act

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Olá Mundo!'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={'username': 'luiz', 'password': '123', 'email': 'tst@test.com'},
    )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'username': 'luiz',
        'email': 'tst@test.com',
        'id': 1,
    }


def test_get_user(client):
    response = client.get('/user/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'luiz',
        'email': 'tst@test.com',
        'id': 1,
    }


def test_get_user_not_found(client):
    response = client.get('/user/2')

    assert response.json() == {'detail': 'user not found'}


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'username': 'luiz', 'email': 'tst@test.com', 'id': 1}]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'password': '123',
            'username': 'test2',
            'email': 'tst@test.com',
            'id': 1,
        },
    )

    assert response.json() == {
        'username': 'test2',
        'email': 'tst@test.com',
        'id': 1,
    }


def test_put_user_not_found(client):
    response = client.put(
        '/users/2',
        json={
            'password': '123',
            'username': 'test2',
            'email': 'tst@test.com',
            'id': 1,
        },
    )

    assert response.json() == {'detail': 'user not found'}


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.json() == {'message': 'User-deleted'}


def test_delete_user_not_found(client):
    response = client.delete('/users/2')

    assert response.json() == {'detail': 'user not found'}
