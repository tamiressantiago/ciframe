# -*- coding: utf-8 -*-
import os
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

import main


def fetch_sequencias(db_path):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute('SELECT id, acordes FROM sequencias ORDER BY id').fetchall()
    finally:
        conn.close()


def test_db_path_respeita_variavel_de_ambiente():
    assert main.DB_PATH == os.environ['CIFRAME_DB_PATH']


def test_init_cria_diretorio_e_arquivo(tmp_path, monkeypatch):
    path = tmp_path / 'aninhado' / 'data' / 'sequencias.db'
    monkeypatch.setattr(main, 'DB_PATH', str(path))

    main.init_db_sequencias()

    assert path.exists()


def test_init_e_idempotente_e_nao_duplica_originais(db_path):
    main.init_db_sequencias()
    main.init_db_sequencias()

    assert fetch_sequencias(db_path) == list(main.SEQUENCIAS_ORIGINAIS)


def test_init_preserva_sequencias_customizadas(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("INSERT INTO sequencias (acordes) VALUES ('Dm G C Am')")
        conn.commit()
    finally:
        conn.close()

    main.init_db_sequencias()

    acordes = [row[1] for row in fetch_sequencias(db_path)]
    assert 'Dm G C Am' in acordes
    assert len(acordes) == len(main.SEQUENCIAS_ORIGINAIS) + 1


def test_acordes_sao_unicos(db_path):
    conn = sqlite3.connect(db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO sequencias (acordes) VALUES ('Bm G D A')")
    finally:
        conn.close()


def test_customizada_persiste_apos_reabrir_banco(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("INSERT INTO sequencias (acordes) VALUES ('Dm G C Am')")
        conn.commit()
    finally:
        conn.close()

    main.init_db_sequencias()
    reaberto = fetch_sequencias(db_path)

    assert ('Dm G C Am',) in [(row[1],) for row in reaberto]


def test_posts_concorrentes_na_mesma_sequencia(client, db_path):
    barreira = threading.Barrier(2)

    def cadastrar(_):
        barreira.wait()
        return main.app.test_client().post(
            '/sequencias', json={'acordes': 'Dm G C Am'}).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        status = sorted(executor.map(cadastrar, range(2)))

    assert status == [201, 409]
    registros = [row for row in fetch_sequencias(db_path) if row[1] == 'Dm G C Am']
    assert len(registros) == 1
