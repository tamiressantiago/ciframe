# Research: hardcoded sequences vs precomputed SEQ_FAMOSA tags

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte).

## Resumo (3-6 sentenças)
As 6 sequências hardcoded em `main.py:40-45` são um mapa `sequencia_concatenada -> id_numérico`. Quando a requisição usa `sequencia_tag`, o código concatena os caracteres recebidos (`sequencia_tag.replace(',','')`) e, se essa string existir no dicionário `sequencias`, obtém `id_seq`. A comparação não é feita diretamente entre a string da sequência e algum campo da música; em vez disso, `get_similares_por_sequencia(id_seq, generos_key)` filtra por gênero e seleciona músicas onde `str(id_seq)` está presente em `musica.seqs_famosas` (campo populado a partir da coluna `SEQ_FAMOSA` do CSV). O campo `seqs_famosas` vem pré-computado do CSV (split por `;`) e é armazenado em `Musica.seqs_famosas` (`musica.py:22`). Portanto, a afirmação é parcialmente correta: existe uma tag pré-computada vinda do CSV, mas a comparação usa o id mapeado pelas 6 sequências hardcoded, não a string da sequência diretamente contra tags textuais.

## Detalhes por componente/área

### Mapa hardcoded
- `main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```
São exatamente 6 entradas, chaves = sequência de acordes concatenados, valores = ids numéricos 0-5.

### Carga do CSV e mapeamento para Musica
- Colunas/index: `ARTISTA_ID=0, MUSICA_ID=1, ARTISTA=2, MUSICA=3, GENERO=4, POPULARIDADE=5, TOM=6, SEQ_FAMOSA=7, CIFRA=8` (`main.py:27-38`).
- Leitura: abre `data/top/dataset_final.csv`, pula header (`main.py:66-69`).
- Para cada linha: `musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")` (`main.py:91`). 
- Criação do objeto: `musica_obj = Musica(..., musica[SEQ_FAMOSA], musica[TOM], musica[CIFRA])` (`main.py:103-106`).
- `Musica` armazena: `self.seqs_famosas = seqs_famosas` (`musica.py:22`). Também computa `self.acordes = list(set(cifra))` (`musica.py:21`) e `self.id_unico_musica`, `self.url`.

### Fluxo em /similares com sequencia_tag
- Rota `/similares` (`main.py:225-247`):
  - Lê params: `acordes_tag`, `id_musica_tag`, `sequencia_tag`, `pagina_tag`, `generos_tag`.
  - Se `sequencia_tag` presente: `acordes = sequencia_tag.replace(',','')` (linha ~240). 
  - `if acordes in sequencias:` obtém `id_seq = sequencias[acordes]` (linha ~243). 
  - Chama `get_similares_por_sequencia(id_seq, generos_key)` e retorna paginado (`main.py:244-246`).
- Função `get_similares_por_sequencia(id_seq, generos_key)` (`main.py:249-273`):
  - `collection = apply_filtro(musicas.values(), generos_key)` (filtra por gênero via `genero_musicas`).
  - Para cada `musica` em coleção: `if str(id_seq) in musica.seqs_famosas: ...` adiciona similar com campos (incluindo `acordes`, `popularidade`, etc.) (`main.py:259-273`).

### Fluxo alternativo (sem sequencia_tag)
- Se vem `acordes_tag` → split por `,` para lista de acordes.
- Se vem `id_musica_tag` → usa `musicas[id_musica_tag].acordes`.
- Caso contrário usa `acordes` recebido. Então chama `get_similares(acordes, generos_key, id_musica_tag)` (`main.py:247`). `get_similares` faz interseção/diferença entre conjuntos de acordes e ordena por `(len(diferenca), -len(intersecao))` (`main.py:303-349`).

## Conexões e fluxos de dados
1. `data/top/dataset_final.csv` (coluna 7 `SEQ_FAMOSA`) → lido em `main.py:69-106` → `musica[SEQ_FAMOSA].split(';')` → passado a `Musica` → `Musica.seqs_famosas` (`musica.py:22`).
2. Cliente chama `/similares?sequencia=BmGDA,...` (sem vírgulas) → `sequencia_tag` → normalizado removendo vírgulas → lookup em `main.py:40-45` → `id_seq` numérico → `get_similares_por_sequencia` → busca `str(id_seq)` em `seqs_famosas` de cada música → retorna paginado.
3. Músicas indexadas em `musicas_dict`/`musicas` (OrderedDict por popularidade) e `genero_musicas` para filtro.

## Resposta direta à pergunta
Hoje, **não é** uma comparação direta das 6 strings hardcoded contra a tag pré-computada. As 6 sequências em `main.py:40-45` são chaves de um mapa para ids numéricos. A tag pré-computada vem do CSV em `SEQ_FAMOSA` (split por `;`, `main.py:91`) e fica em `Musica.seqs_famosas` (`musica.py:22`). Em `/similares` com `sequencia_tag`, o valor sem vírgulas é procurado nas chaves do dicionário para obter `id_seq` (`main.py:240-246`); `get_similares_por_sequencia` então filtra por gênero e retorna músicas cujo `musica.seqs_famosas` contém `str(id_seq)` (`main.py:259-273`). Ou seja: mapeamento hardcoded (sequência string -> id) + busca por id nas tags pré-computadas do CSV.
