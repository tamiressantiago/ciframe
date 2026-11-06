# coding: utf-8
import json
from flask import Flask, request
import sys
from musica import *
from collections import OrderedDict
import unicodedata
import sqlite3
import os

app = Flask(__name__)

DB_DIR = os.path.join('data', 'db')
DB_PATH = os.environ.get('CIFRAME_DB_PATH', os.path.join(DB_DIR, 'sequencias.db'))

SEQUENCIAS_ORIGINAIS = [
    (0, 'Bm G D A'),
    (1, 'C G Am F'),
    (2, 'Em G'),
    (3, 'C A7 Dm G7'),
    (4, 'Gm F'),
    (5, 'C C7 F Fm'),
]


def init_db_sequencias():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS sequencias (
        id INTEGER PRIMARY KEY,
        acordes TEXT UNIQUE
    )''')
    for seq_id, acordes_str in SEQUENCIAS_ORIGINAIS:
        cur.execute('INSERT OR IGNORE INTO sequencias (id, acordes) VALUES (?, ?)', (seq_id, acordes_str))
    conn.commit()
    conn.close()


init_db_sequencias()

def limpa_cifra(raw_cifra):
    cifra = []
    for m in raw_cifra:
        if m.strip() != '':
            # filtra tablaturas
            if '|' in m:
                acorde = m.split('|')[0].split()[0]
                cifra.append(acorde)
            # lida com acordes separados por espaço
            else:
                tokens = [token for token in m.split()]
                cifra += tokens
    return cifra


def normalizar_sequencia(texto):
    if not isinstance(texto, str):
        return ''
    tokens = texto.replace(',', ' ').split()
    return ' '.join(token[0].upper() + token[1:] for token in tokens)

# colunas do csv
ARTISTA_ID = 0
MUSICA_ID = 1
ARTISTA = 2
MUSICA = 3
GENERO = 4
POPULARIDADE = 5
TOM = 6
SEQ_FAMOSA = 7
CIFRA = 8
TAM_PAGINA = 100
MAX_ACORDES_SEQUENCIA = 20
MAX_CARACTERES_ACORDE = 30
MAX_CONTEUDO_SEQUENCIA = 2 * 1024

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTEUDO_SEQUENCIA

genero_musicas = {}
generos = set()
acordes = set()


def has_exact_consecutive_sequence(cifra_list, seq_tokens):
    if len(seq_tokens) == 0:
        return False
    if len(seq_tokens) > len(cifra_list):
        return False
    for i in range(len(cifra_list) - len(seq_tokens) + 1):
        match = True
        for j in range(len(seq_tokens)):
            if cifra_list[i + j].strip() != seq_tokens[j]:
                match = False
                break
        if match:
            return True
    return False


def musica_contem_sequencia(cifra, seq_tokens):
    if not has_exact_consecutive_sequence(cifra, seq_tokens):
        return False
    seq_chords_set = set(seq_tokens)
    cifra_chords_set = set([c.strip() for c in cifra if str(c).strip() != ''])
    extra = cifra_chords_set - seq_chords_set
    if len(extra) == 0:
        return True
    return False


def musica_tem_sequencia(musica, seq_tokens):
    cifra = getattr(musica, 'cifra', None)
    if cifra is None:
        return False
    return musica_contem_sequencia(cifra, seq_tokens)


musicas_dict = {}

f = open('data/top/dataset_final.csv', encoding='utf-8')
f.readline()

for line in f:
    line = line.replace('"', '').replace('NA', '')[:-1]

    musica = line.split(',')
    musica[POPULARIDADE] = int(musica[POPULARIDADE].replace('.', ''))

    if musica[CIFRA] != '':
        musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))
    else:
        musica[CIFRA] = []

    musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")

    # conjunto único de gêneros
    generos.add(musica[GENERO])

    # inclui música no dict de músicas
    musica_obj = Musica(musica[ARTISTA_ID], musica[ARTISTA],
            musica[MUSICA_ID], musica[MUSICA], musica[GENERO],
            int(musica[POPULARIDADE]), musica[SEQ_FAMOSA],
            musica[TOM], musica[CIFRA])

    musicas_dict[musica_obj.id_unico_musica] = musica_obj

    # conjunto único de acordes
    for acorde in musica_obj.acordes:
        acordes.add(acorde)

    # constrói dict mapeando gênero para músicas
    # deve ser usado para melhorar o desempenho das buscas
    if musica_obj.genero in genero_musicas:
        genero_musicas[musica_obj.genero].append(musica_obj)
    else:
        genero_musicas[musica_obj.genero] = [musica_obj]

# dicionário de músicas cujos valores são ordenados por popularidade
musicas = OrderedDict(sorted(musicas_dict.items(),
    key=lambda x: x[1].popularidade, reverse = True))

# para trabalhar melhor com json
generos = list(generos)

# ordena genero_musicas por popularidade
for k,v in genero_musicas.items():
    genero_musicas[k].sort(key = lambda x : x.popularidade, reverse = True)

f.close()


@app.route('/')
def index():
    return app.send_static_file('index.html')
''' Busca por músicas que possuem no título ou no nome do artista o argumento passado por key.
params: key e generos (opcional). Caso generos não sejam definidos, a busca não irá filtrar por gênero.
exemplo 1: /search?key=no dia em que eu saí de casa
exemplo 2: /search?key=no dia em que eu saí de casa&generos=Rock,Samba '''

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

@app.route('/search')
def busca():
    generos_tag = request.args.get('generos', [])
    pagina_tag = request.args.get('pagina','1')
    keys = request.args.get('key').lower()
    keys = remover_combinantes(keys).split(' ')

    generos_key = generos
    if generos_tag:
        generos_key = generos_tag.split(',')

    collection = apply_filtro(musicas.values(), generos_key)
    out = []

    for musica in collection:
        text = '%s %s' % (musica.nome_artista.lower(), musica.nome_musica.lower())
        text_list = remover_combinantes(text).split(' ')
        if all(key in text_list for key in keys):
            matches = {
                'id_unico_musica' : musica.id_unico_musica,
                'id_artista' : musica.id_artista,
                'id_musica' : musica.id_musica,
                'nome_artista' : musica.nome_artista,
                'nome_musica' : musica.nome_musica,
                'genero' : musica.genero,
                'url' : musica.url,
            }
            out.append(matches)
    return json.dumps(get_pagina(out, pagina_tag))

# cópia
def remover_combinantes(string):
    string = unicodedata.normalize('NFD', string)
    return u''.join(ch for ch in string if unicodedata.category(ch) != 'Mn')

''' Retorna as músicas armazenadas no sistema (ordenados por popularidade).
    O serviço é paginado. Cada página tem tamanho 100, por default.
    params: pagina. Caso não seja definida a página, o valor default é 1.
    exemplo 1: /musica?pagina=2
    exemplo 2: /musica'''
@app.route('/musicas')
def get_musicas():
    return json.dumps([v.__dict__ for v in musicas.values()])

@app.route('/generos')
def get_generos():
    return json.dumps(generos)

@app.route('/acordes')
def get_acordes():
    return json.dumps(list(acordes))

@app.route('/sequencias', methods=['GET'])
def get_sequencias():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        try:
            cur = conn.cursor()
            cur.execute('SELECT id, acordes FROM sequencias ORDER BY id')
            resultado = [{'id': row[0], 'acordes': row[1]} for row in cur.fetchall()]
        finally:
            conn.close()
    except sqlite3.Error:
        return json.dumps({'erro': 'erro ao acessar banco de sequencias'}), 500
    return json.dumps(resultado)

@app.route('/sequencias', methods=['POST'])
def post_sequencias():
    if request.content_length is not None and request.content_length > MAX_CONTEUDO_SEQUENCIA:
        return json.dumps({'erro': 'corpo muito grande'}), 413

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return json.dumps({'erro': 'corpo invalido'}), 400

    acordes_raw = data.get('acordes')
    if not isinstance(acordes_raw, str):
        return json.dumps({'erro': 'acordes deve ser string'}), 400

    acordes_normalizados = normalizar_sequencia(acordes_raw)
    if not acordes_normalizados:
        return json.dumps({'erro': 'sequencia vazia'}), 400

    tokens = acordes_normalizados.split(' ')
    if len(tokens) > MAX_ACORDES_SEQUENCIA:
        return json.dumps({
            'erro': 'sequencia pode ter no maximo %d acordes' % MAX_ACORDES_SEQUENCIA
        }), 400
    if any(len(token) > MAX_CARACTERES_ACORDE for token in tokens):
        return json.dumps({
            'erro': 'cada acorde pode ter no maximo %d caracteres' % MAX_CARACTERES_ACORDE
        }), 400

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO sequencias (acordes) VALUES (?)', (acordes_normalizados,))
            conn.commit()
            novo_id = cur.lastrowid
        except sqlite3.IntegrityError:
            conn.rollback()
            cur.execute('SELECT id FROM sequencias WHERE acordes = ?', (acordes_normalizados,))
            row = cur.fetchone()
            if row is None:
                return json.dumps({'erro': 'sequencia ja existe'}), 409
            return json.dumps({'erro': 'sequencia ja existe', 'id': row[0]}), 409
    except sqlite3.Error:
        return json.dumps({'erro': 'erro ao acessar banco de sequencias'}), 500
    finally:
        if conn is not None:
            conn.close()

    return json.dumps({'id': novo_id, 'acordes': acordes_normalizados}), 201

@app.route('/musica/<m_id>/')
def get_musica(m_id):
    return json.dumps(musicas[m_id].__dict__)

@app.route('/similares')
def get_similares():
    # tratando request
    acordes_tag = request.args.get('acordes')
    id_musica_tag = request.args.get('id_unico_musica')
    sequencia_tag = request.args.get('sequencia')
    pagina_tag = request.args.get('pagina','1')

    # se não existir, filtra por todos.
    generos_tag = request.args.get('generos')
    generos_key = generos
    if generos_tag:
        generos_key = generos_tag.split(',')

    acordes = []
    if acordes_tag:
        acordes = acordes_tag.split(',')
    elif id_musica_tag:
        musica = musicas[id_musica_tag]
        acordes = musica.acordes
    elif sequencia_tag:
        acordes_sequencia = normalizar_sequencia(sequencia_tag)
        if not acordes_sequencia:
            return json.dumps([])

        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            try:
                cur = conn.cursor()
                cur.execute('SELECT id FROM sequencias WHERE acordes = ?', (acordes_sequencia,))
                sequencia_existe = cur.fetchone() is not None
            finally:
                conn.close()
        except sqlite3.Error:
            return json.dumps({'erro': 'erro ao acessar banco de sequencias'}), 500

        if not sequencia_existe:
            return json.dumps([])

        similares = get_similares_por_sequencia(acordes_sequencia.split(' '), generos_key)
        return json.dumps(get_pagina(similares, pagina_tag))

    similares = get_similares(acordes, generos_key, id_musica_tag)

    return json.dumps(get_pagina(similares, pagina_tag))

def get_similares_por_sequencia(seq_tokens, generos_key):
    # filtra para melhor desempenho
    collection = apply_filtro(musicas.values(), generos_key)

    similares = []
    for musica in collection:
        if musica_tem_sequencia(musica, seq_tokens):
            similar = {
                'id_unico_musica' : musica.id_unico_musica,
                'id_artista' : musica.id_artista,
                'id_musica' : musica.id_musica,
                'nome_artista' : musica.nome_artista,
                'nome_musica' : musica.nome_musica,
                'popularidade' : musica.popularidade,
                'acordes' : musica.acordes,
                'genero' : musica.genero,
                'url' : musica.url,
            }
            similares.append(similar)

    return similares


def get_pagina(colecao, pagina_tag):
    sl = (int(pagina_tag) - 1)*TAM_PAGINA
    return colecao[sl:sl+TAM_PAGINA]

def get_similares(acordes, generos_key, id_musica = None):

    # filtra para melhor desempenho
    collection = apply_filtro(musicas.values(), generos_key)

    similares = []
    for musica in collection:

        if musica.id_unico_musica != id_musica:

            inter = set(acordes).intersection(set(musica.acordes))
            diff = set(musica.acordes) - set(acordes)

            # somente as que tiverem interseção e as que forem
            # dos generos solicitados.
            if len(inter) > 0:
                similar = {
                        'id_unico_musica' : musica.id_unico_musica,
                        'id_artista' : musica.id_artista,
                        'id_musica' : musica.id_musica,
                        'nome_artista' : musica.nome_artista,
                        'nome_musica' : musica.nome_musica,
                        'popularidade' : musica.popularidade,
                        'acordes' : musica.acordes,
                        'genero' : musica.genero,
                        'url' : musica.url,
                        'diferenca' : list(diff),
                        'intersecao' : list(inter)
                }

                similares.append(similar)

    # ordenados por menor diferença, maior interseção e maior popularidade.
    return sorted(similares, key=lambda x: (len(x['diferenca']), -len(x['intersecao'])))

## Filtra a coleção de músicas por gênero.
def apply_filtro(musicas, generos_key):
    # filtra para melhor desempenho
    collection = []
    for genero in generos_key:
        if genero in generos:
            collection += genero_musicas[genero]
    return collection

@app.errorhandler(413)
def corpo_muito_grande(error):
    return json.dumps({'erro': 'corpo muito grande'}), 413

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=True)
