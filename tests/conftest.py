# -*- coding: utf-8 -*-
import atexit
import json
import os
import shutil
import sys
import tempfile
from collections import OrderedDict

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

_SESSION_DB_DIR = tempfile.mkdtemp(prefix='ciframe-tests-')
atexit.register(shutil.rmtree, _SESSION_DB_DIR, ignore_errors=True)
os.environ['CIFRAME_DB_PATH'] = os.path.join(_SESSION_DB_DIR, 'sequencias.db')

import main  # noqa: E402  (precisa ser importado depois do sys.path/env)


@pytest.fixture()
def json_response():
    def parse(response):
        return json.loads(response.get_data(as_text=True))

    return parse


@pytest.fixture()
def db_path(tmp_path, monkeypatch):
    path = str(tmp_path / 'sequencias.db')
    monkeypatch.setattr(main, 'DB_PATH', path)
    main.init_db_sequencias()
    return path


@pytest.fixture()
def client(db_path):
    main.app.config['TESTING'] = True
    with main.app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def musica_factory():
    def create(id_musica, cifra, genero='Rock', popularidade=100):
        return main.Musica(
            'artista_%s' % id_musica,
            'Artista %s' % id_musica,
            id_musica,
            'Musica %s' % id_musica,
            genero,
            popularidade,
            [],
            'C',
            list(cifra),
        )

    return create


@pytest.fixture()
def catalogo_sintetico(monkeypatch, musica_factory):
    r1 = musica_factory('r1', ['C', 'G', 'Am', 'F'], 'Rock', 100)
    r2 = musica_factory('r2', ['C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F'], 'Rock', 90)
    r3 = musica_factory('r3', ['C', 'G', 'Am', 'F', 'Dm'], 'Rock', 80)
    r4 = musica_factory('r4', ['C', 'G', 'Am'], 'Rock', 70)
    r5 = musica_factory('r5', ['C', 'G', 'Am', 'C'], 'Rock', 60)
    r6 = musica_factory('r6', ['F#m', 'D', 'A', 'E'], 'Rock', 55)
    s1 = musica_factory('s1', ['Am', 'F', 'C', 'G'], 'Samba', 50)
    s2 = musica_factory('s2', ['C', 'G', 'Am', 'F'], 'Samba', 40)
    s3 = musica_factory('s3', ['C', 'G', 'F'], 'Samba', 30)

    todas = [r1, r2, r3, r4, r5, r6, s1, s2, s3]
    musicas = OrderedDict((m.id_unico_musica, m) for m in todas)
    genero_musicas = {
        'Rock': [r1, r2, r3, r4, r5, r6],
        'Samba': [s1, s2, s3],
    }

    monkeypatch.setattr(main, 'musicas', musicas)
    monkeypatch.setattr(main, 'genero_musicas', genero_musicas)
    monkeypatch.setattr(main, 'generos', ['Rock', 'Samba'])

    return {
        'todas': todas,
        'rock': [r1, r2, r3, r4, r5, r6],
        'samba': [s1, s2, s3],
        'r1': r1,
        'r2': r2,
        'r4': r4,
        'r5': r5,
        'r6': r6,
        's2': s2,
    }
