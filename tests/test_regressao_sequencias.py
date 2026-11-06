# -*- coding: utf-8 -*-
import json
import os

import main


FIXTURE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'fixtures',
    'similares_sequencias_baseline.json',
)

SEQUENCIAS = [
    (['Bm', 'G', 'D', 'A'], 0),
    (['C', 'G', 'Am', 'F'], 1),
    (['Em', 'G'], 2),
    (['C', 'A7', 'Dm', 'G7'], 3),
    (['Gm', 'F'], 4),
    (['C', 'C7', 'F', 'Fm'], 5),
]


def carregar_baseline():
    with open(FIXTURE_PATH, encoding='utf-8') as arquivo:
        return json.load(arquivo)


def ids(pagina):
    return [musica['id_unico_musica'] for musica in pagina]


def test_baseline_compativel_com_o_catalogo():
    baseline = carregar_baseline()

    assert main.TAM_PAGINA == baseline['tam_pagina']
    assert len(baseline['sequencias']) == len(SEQUENCIAS)
    assert [entry['id'] for entry in baseline['sequencias']] == [
        seq_id for _, seq_id in SEQUENCIAS]


def test_regressao_6_sequencias_conjuntos_identicos():
    for seq_tokens, seq_id in SEQUENCIAS:
        esperados = set()
        for mid, musica in main.musicas.items():
            if any(str(sf).strip() == str(seq_id) for sf in musica.seqs_famosas):
                esperados.add(mid)

        encontrados = set()
        for mid, musica in main.musicas.items():
            if main.musica_contem_sequencia(musica.cifra, seq_tokens):
                encontrados.add(mid)

        assert encontrados == esperados, (
            'Diferenca para sequencia %s (id=%s)' % (seq_tokens, seq_id))


def test_regressao_6_sequencias_ordem_e_paginas(client, json_response):
    baseline = carregar_baseline()

    for entry in baseline['sequencias']:
        total_encontrado = 0
        for numero_pagina, pagina_esperada in enumerate(entry['paginas'], start=1):
            response = client.get('/similares', query_string={
                'sequencia': entry['sequencia'],
                'pagina': str(numero_pagina),
                'generos': ','.join(baseline['generos_ordem']),
            })
            assert response.status_code == 200
            pagina = json_response(response)
            total_encontrado += len(pagina)
            assert ids(pagina) == pagina_esperada, (
                'Diferenca para sequencia %s (id=%s), pagina %s' % (
                    entry['sequencia'], entry['id'], numero_pagina))
        assert total_encontrado == entry['total'], (
            'Total diverge para sequencia %s (id=%s)' % (
                entry['sequencia'], entry['id']))
