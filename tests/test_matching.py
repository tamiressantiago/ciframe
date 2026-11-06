# -*- coding: utf-8 -*-
import pytest

import main


@pytest.mark.parametrize('entrada, esperado', [
    ('C,G,Am,F', 'C G Am F'),
    ('C G Am F', 'C G Am F'),
    ('C, G , Am ,F', 'C G Am F'),
    ('  C   G  ', 'C G'),
    ('bm,g,d,a', 'Bm G D A'),
    ('c#m d#', 'C#m D#'),
    ('cmaj7, f7', 'Cmaj7 F7'),
    ('G,Bm,D,A,G', 'G Bm D A G'),
])
def test_normalizar_sequencia_formatos(entrada, esperado):
    assert main.normalizar_sequencia(entrada) == esperado


@pytest.mark.parametrize('entrada', [
    '',
    '   ',
    ',',
    ' , , ',
    None,
    123,
    ['C', 'G'],
])
def test_normalizar_sequencia_entradas_invalidas(entrada):
    assert main.normalizar_sequencia(entrada) == ''


@pytest.mark.parametrize('cifra, seq, esperado', [
    (['C', 'G', 'Am', 'F'], ['C', 'G', 'Am', 'F'], True),
    (['C', 'G', 'Am', 'F'], ['G', 'Am'], True),
    (['C', 'G', 'Am', 'F'], ['Am', 'F'], True),
    (['C', 'G', 'Am', 'F'], ['Am', 'C'], False),
    (['C', 'C', 'G', 'C'], ['C', 'G'], True),
    (['C', 'G'], ['C', 'G', 'Am'], False),
    (['C', 'G'], [], False),
    ([' C ', 'G'], ['C', 'G'], True),
])
def test_has_exact_consecutive_sequence(cifra, seq, esperado):
    assert main.has_exact_consecutive_sequence(cifra, seq) is esperado


def test_musica_contem_sequencia_rejeita_acorde_fora_da_sequencia():
    assert main.musica_contem_sequencia(
        ['C', 'G', 'Am', 'Dm'], ['C', 'G', 'Am']) is False


def test_musica_contem_sequencia_rejeita_ordem_diferente():
    assert main.musica_contem_sequencia(
        ['C', 'G', 'Am'], ['G', 'C', 'Am']) is False


def test_musica_contem_sequencia_aceita_repeticao_do_acorde():
    assert main.musica_contem_sequencia(
        ['C', 'G', 'Am', 'C', 'G'], ['C', 'G', 'Am']) is True


def test_musica_contem_sequencia_ignora_acordes_vazios():
    assert main.musica_contem_sequencia(
        ['C', 'G', 'Am', ''], ['C', 'G', 'Am']) is True


def test_musica_contem_sequencia_vazia_nao_casa():
    assert main.musica_contem_sequencia(['C', 'G'], []) is False


def test_musica_tem_sequencia_com_musica(musica_factory):
    musica = musica_factory('m1', ['C', 'G', 'Am', 'F'])
    assert main.musica_tem_sequencia(musica, ['C', 'G', 'Am', 'F']) is True
    assert main.musica_tem_sequencia(musica, ['C', 'G', 'Am']) is False
    assert main.musica_tem_sequencia(musica, ['C', 'G', 'Dm']) is False


def test_musica_tem_sequencia_sem_atributos():
    class SemCifra(object):
        pass

    assert main.musica_tem_sequencia(SemCifra(), ['C']) is False


def test_musica_tem_sequencia_nao_depende_da_tag_do_csv(musica_factory):
    musica = musica_factory('m2', ['C', 'G', 'Am'])
    musica.seqs_famosas = ['0', '1', '2']
    assert main.musica_tem_sequencia(musica, ['C', 'G', 'Am']) is True
    assert main.musica_tem_sequencia(musica, ['C', 'G']) is False
    assert main.musica_tem_sequencia(musica, ['C', 'Am']) is False
