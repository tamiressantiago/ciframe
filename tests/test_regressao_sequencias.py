# -*- coding: utf-8 -*-
import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules['flask'] = MagicMock()

from musica import Musica
from main import limpa_cifra, musica_contem_sequencia

ARTISTA_ID = 0
MUSICA_ID = 1
ARTISTA = 2
MUSICA = 3
GENERO = 4
POPULARIDADE = 5
TOM = 6
SEQ_FAMOSA = 7
CIFRA = 8

sequencias = [
    (['Bm', 'G', 'D', 'A'], 0),
    (['C', 'G', 'Am', 'F'], 1),
    (['Em', 'G'], 2),
    (['C', 'A7', 'Dm', 'G7'], 3),
    (['Gm', 'F'], 4),
    (['C', 'C7', 'F', 'Fm'], 5),
]


class TestRegressaoSequencias(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'data', 'top', 'dataset_final.csv')
        cls.musicas_dict = {}
        with open(csv_path, 'r', encoding='utf-8') as f:
            f.readline()
            for line in f:
                try:
                    line = line.replace('"', '').replace('NA', '')[:-1]
                except Exception:
                    continue
                musica = line.split(',')
                if len(musica) < 9:
                    continue
                try:
                    musica[POPULARIDADE] = int(str(musica[POPULARIDADE]).replace('.', ''))
                except Exception:
                    musica[POPULARIDADE] = 0
                if musica[CIFRA] != '':
                    musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))
                else:
                    musica[CIFRA] = []
                musica[SEQ_FAMOSA] = str(musica[SEQ_FAMOSA]).split(';')
                musica_obj = Musica(musica[ARTISTA_ID], musica[ARTISTA],
                                    musica[MUSICA_ID], musica[MUSICA], musica[GENERO],
                                    int(musica[POPULARIDADE]), musica[SEQ_FAMOSA],
                                    musica[TOM], musica[CIFRA])
                cls.musicas_dict[musica_obj.id_unico_musica] = musica_obj

    def test_regressao_6_sequencias_conjuntos_identicos(self):
        for seq_tokens, seq_id in sequencias:
            esperados = set()
            for mid, m in self.musicas_dict.items():
                for sf in m.seqs_famosas:
                    sf_clean = str(sf).strip()
                    if sf_clean == str(seq_id):
                        esperados.add(mid)
                        break
            encontrados = set()
            for mid, m in self.musicas_dict.items():
                if musica_contem_sequencia(m.cifra, seq_tokens):
                    encontrados.add(mid)
            self.assertEqual(esperados, encontrados,
                             msg='Diferenca para sequencia %s (id=%s)' % (seq_tokens, seq_id))


if __name__ == '__main__':
    unittest.main()
