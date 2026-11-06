# -*- coding: utf-8 -*-
import sqlite3

import pytest

import main


ORIGINAIS = [
    (0, 'Bm G D A'),
    (1, 'C G Am F'),
    (2, 'Em G'),
    (3, 'C A7 Dm G7'),
    (4, 'Gm F'),
    (5, 'C C7 F Fm'),
]


def test_get_sequencias_retorna_as_originais_na_ordem(client, json_response):
    response = client.get('/sequencias')

    assert response.status_code == 200
    assert json_response(response) == [
        {'id': seq_id, 'acordes': acordes} for seq_id, acordes in ORIGINAIS
    ]


def test_get_sequencias_mantem_content_type_e_cors_legados(client):
    response = client.get('/sequencias')

    assert response.mimetype == 'text/html'
    assert response.headers['Access-Control-Allow-Origin'] == '*'


def test_get_sequencias_inclui_sequencia_cadastrada(client, json_response):
    criada = client.post('/sequencias', json={'acordes': 'Dm G C Am'})

    response = client.get('/sequencias')
    sequencias = json_response(response)

    assert criada.status_code == 201
    assert {'id': json_response(criada)['id'], 'acordes': 'Dm G C Am'} in sequencias


def test_get_sequencias_rota_tem_precedencia_sobre_arquivo_estatico(client, json_response):
    response = client.get('/sequencias')

    assert response.status_code == 200
    assert isinstance(json_response(response), list)


def test_get_sequencias_erro_de_banco_retorna_500(client, json_response, monkeypatch):
    def falhar(*args, **kwargs):
        raise sqlite3.OperationalError('indisponivel')

    monkeypatch.setattr(main.sqlite3, 'connect', falhar)

    response = client.get('/sequencias')

    assert response.status_code == 500
    assert json_response(response) == {'erro': 'erro ao acessar banco de sequencias'}


def test_post_sequencias_cria_com_201(client, json_response):
    response = client.post('/sequencias', json={'acordes': 'Dm G C Am'})

    assert response.status_code == 201
    body = json_response(response)
    assert body == {'id': body['id'], 'acordes': 'Dm G C Am'}
    assert isinstance(body['id'], int)


def test_post_sequencias_normaliza_entrada(client, json_response):
    response = client.post('/sequencias', json={'acordes': '  dm ,G, c , am '})

    assert response.status_code == 201
    assert json_response(response)['acordes'] == 'Dm G C Am'


def test_post_sequencias_aceita_acorde_com_sustenido(client, json_response):
    response = client.post('/sequencias', json={'acordes': 'F#m,D,A,E'})

    assert response.status_code == 201
    assert json_response(response)['acordes'] == 'F#m D A E'


def test_post_sequencias_aceita_acorde_desconhecido(client, json_response):
    response = client.post('/sequencias', json={'acordes': 'Xyz Abc'})

    assert response.status_code == 201
    assert json_response(response)['acordes'] == 'Xyz Abc'


def test_post_sequencias_duplicata_exata_retorna_409(client, json_response):
    client.post('/sequencias', json={'acordes': 'Dm G C Am'})
    response = client.post('/sequencias', json={'acordes': 'Dm G C Am'})

    assert response.status_code == 409
    assert json_response(response)['erro'] == 'sequencia ja existe'
    assert isinstance(json_response(response)['id'], int)


def test_post_sequencias_duplicata_de_original_retorna_id_existente(client, json_response):
    response = client.post('/sequencias', json={'acordes': 'bm,g,d,a'})

    assert response.status_code == 409
    assert json_response(response) == {'erro': 'sequencia ja existe', 'id': 0}


@pytest.mark.parametrize('payload', [
    {},
    {'acordes': None},
    {'acordes': 123},
    {'acordes': ['C', 'G']},
    {'acordes': ''},
    {'acordes': '   '},
    {'acordes': ' , , '},
])
def test_post_sequencias_payload_invalido_retorna_400(client, json_response, payload):
    response = client.post('/sequencias', json=payload)

    assert response.status_code == 400
    assert 'erro' in json_response(response)


def test_post_sequencias_sem_json_retorna_400(client, json_response):
    response = client.post('/sequencias', data='', content_type='text/plain')

    assert response.status_code == 400
    assert json_response(response) == {'erro': 'corpo invalido'}


def test_post_sequencias_json_malformado_retorna_400(client, json_response):
    response = client.post(
        '/sequencias', data='{invalido', content_type='application/json')

    assert response.status_code == 400
    assert json_response(response) == {'erro': 'corpo invalido'}


def test_post_sequencias_erro_de_banco_retorna_500(client, json_response, monkeypatch):
    def falhar(*args, **kwargs):
        raise sqlite3.OperationalError('indisponivel')

    monkeypatch.setattr(main.sqlite3, 'connect', falhar)

    response = client.post('/sequencias', json={'acordes': 'Dm G C Am'})

    assert response.status_code == 500
    assert json_response(response) == {'erro': 'erro ao acessar banco de sequencias'}


def test_post_sequencias_aceita_20_acordes(client, json_response):
    acordes = ' '.join(['C'] * main.MAX_ACORDES_SEQUENCIA)

    response = client.post('/sequencias', json={'acordes': acordes})

    assert response.status_code == 201
    assert json_response(response)['acordes'] == acordes


def test_post_sequencias_rejeita_21_acordes(client, json_response):
    acordes = ' '.join(['C'] * (main.MAX_ACORDES_SEQUENCIA + 1))

    response = client.post('/sequencias', json={'acordes': acordes})

    assert response.status_code == 400
    assert '20 acordes' in json_response(response)['erro']


def test_post_sequencias_aceita_acorde_com_30_caracteres(client, json_response):
    acorde = 'A' * main.MAX_CARACTERES_ACORDE

    response = client.post('/sequencias', json={'acordes': acorde})

    assert response.status_code == 201
    assert json_response(response)['acordes'] == acorde


def test_post_sequencias_rejeita_acorde_com_31_caracteres(client, json_response):
    acorde = 'A' * (main.MAX_CARACTERES_ACORDE + 1)

    response = client.post('/sequencias', json={'acordes': acorde})

    assert response.status_code == 400
    assert '30 caracteres' in json_response(response)['erro']


def test_post_sequencias_corpo_acima_de_2kb_retorna_413(client, json_response):
    acordes = 'C ' * 1024

    response = client.post('/sequencias', json={'acordes': acordes})

    assert response.status_code == 413
    assert json_response(response) == {'erro': 'corpo muito grande'}
