# -*- coding: utf-8 -*-
import sqlite3

import pytest

import main


def ids(pagina):
    return [musica['id_unico_musica'] for musica in pagina]


def test_similares_sequencia_original_sem_filtro(client, json_response, catalogo_sintetico):
    response = client.get('/similares', query_string={'sequencia': 'C,G,Am,F'})

    assert response.status_code == 200
    assert ids(json_response(response)) == [
        catalogo_sintetico['r1'].id_unico_musica,
        catalogo_sintetico['r2'].id_unico_musica,
        catalogo_sintetico['s2'].id_unico_musica,
    ]


def test_similares_normaliza_separadores_e_caixa(client, json_response, catalogo_sintetico):
    com_virgula = json_response(
        client.get('/similares', query_string={'sequencia': 'C,G,Am,F'}))
    com_espaco = json_response(
        client.get('/similares', query_string={'sequencia': 'c g am f'}))

    assert ids(com_espaco) == ids(com_virgula)


@pytest.mark.parametrize('genero, esperados', [
    ('Rock', ['r1', 'r2']),
    ('Samba', ['s2']),
    ('Genero Inexistente', []),
])
def test_similares_filtra_por_genero(
        client, json_response, catalogo_sintetico, genero, esperados):
    response = client.get(
        '/similares', query_string={'sequencia': 'C G Am F', 'generos': genero})

    assert response.status_code == 200
    assert ids(json_response(response)) == [
        catalogo_sintetico[nome].id_unico_musica for nome in esperados
    ]


def test_similares_sequencia_nao_cadastrada_retorna_vazio(client, json_response, catalogo_sintetico):
    response = client.get('/similares', query_string={'sequencia': 'Dm G C Am'})

    assert response.status_code == 200
    assert json_response(response) == []


def test_similares_sequencia_vazia_retorna_vazio(client, json_response, catalogo_sintetico):
    response = client.get('/similares', query_string={'sequencia': ''})

    assert response.status_code == 200
    assert json_response(response) == []


def test_similares_sequencia_customizada_apos_post(client, json_response, catalogo_sintetico):
    criada = client.post('/sequencias', json={'acordes': 'c,g,am'})
    assert criada.status_code == 201

    response = client.get('/similares', query_string={'sequencia': 'C G Am'})

    assert response.status_code == 200
    assert ids(json_response(response)) == [
        catalogo_sintetico['r4'].id_unico_musica,
        catalogo_sintetico['r5'].id_unico_musica,
    ]


def test_similares_sequencia_customizada_com_sustenido(
        client, json_response, catalogo_sintetico):
    criada = client.post('/sequencias', json={'acordes': 'f#m,d,a,e'})
    assert criada.status_code == 201
    assert json_response(criada)['acordes'] == 'F#m D A E'

    response = client.get(
        '/similares', query_string={'sequencia': 'F#m,D,A,E', 'generos': 'Rock'})

    assert response.status_code == 200
    assert ids(json_response(response)) == [
        catalogo_sintetico['r6'].id_unico_musica,
    ]


def test_similares_customizada_respeita_filtro_de_genero(
        client, json_response, catalogo_sintetico):
    client.post('/sequencias', json={'acordes': 'C G Am'})

    response = client.get(
        '/similares', query_string={'sequencia': 'C G Am', 'generos': 'Samba'})

    assert response.status_code == 200
    assert json_response(response) == []


def test_similares_paginacao(client, json_response, catalogo_sintetico, monkeypatch):
    monkeypatch.setattr(main, 'TAM_PAGINA', 1)

    assert ids(json_response(client.get(
        '/similares', query_string={'sequencia': 'C G Am F', 'pagina': '1'}
    ))) == [catalogo_sintetico['r1'].id_unico_musica]
    assert ids(json_response(client.get(
        '/similares', query_string={'sequencia': 'C G Am F', 'pagina': '2'}
    ))) == [catalogo_sintetico['r2'].id_unico_musica]
    assert ids(json_response(client.get(
        '/similares', query_string={'sequencia': 'C G Am F', 'pagina': '3'}
    ))) == [catalogo_sintetico['s2'].id_unico_musica]
    assert json_response(client.get(
        '/similares', query_string={'sequencia': 'C G Am F', 'pagina': '4'}
    )) == []


def test_similares_formato_do_item(client, json_response, catalogo_sintetico):
    pagina = json_response(
        client.get('/similares', query_string={'sequencia': 'C G Am F'}))
    item = pagina[0]

    assert set(item) == {
        'id_unico_musica', 'id_artista', 'id_musica', 'nome_artista',
        'nome_musica', 'popularidade', 'acordes', 'genero', 'url',
    }
    assert 'diferenca' not in item
    assert 'intersecao' not in item
    assert item['id_unico_musica'] == catalogo_sintetico['r1'].id_unico_musica


def test_similares_erro_de_banco_retorna_500(client, json_response, catalogo_sintetico, monkeypatch):
    def falhar(*args, **kwargs):
        raise sqlite3.OperationalError('indisponivel')

    monkeypatch.setattr(main.sqlite3, 'connect', falhar)

    response = client.get('/similares', query_string={'sequencia': 'C G Am F'})

    assert response.status_code == 500
    assert json_response(response) == {'erro': 'erro ao acessar banco de sequencias'}
