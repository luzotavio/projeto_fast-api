from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app

client = TestClient(app)


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # arrange

    response = client.get('/')  # act

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Olá Mundo!'}


def test_read_html_deve_retornar_html_ola_mundo():
    client = TestClient(app)

    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
