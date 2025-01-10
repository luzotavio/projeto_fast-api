from http import HTTPStatus


def test_read_root_deve_retornar_ok_e_ola_mundo(client):  # arrange
    response = client.get('/')  # act

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Olá Mundo!'}
