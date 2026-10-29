# Research: definição de "a sequência X aparece na música Y"

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte).

## Resumo (3-6 sentenças)
Atualmente, quando se busca por uma das 6 sequências hardcoded via `/similares?sequencia=...`, a definição é puramente por **tag pré-computada**: a string concatenada sem vírgulas é mapeada pelo dicionário `sequencias` (`main.py:40-45`) para um `id_seq` numérico; `get_similares_por_sequencia` (`main.py:249-273`) retorna músicas em que `str(id_seq)` está contido em `musica.seqs_famosas`. As tags vêm da coluna `SEQ_FAMOSA` do CSV, separadas por `;` (`main.py:91`) e armazenadas como lista em `Musica.seqs_famosas` (`musica.py:22`). Não há lógica no código-fonte atual para extrair sequência da cifra, comparar ordem/repetições, ou normalizar acordes no caminho da busca por sequência; essa comparação é uma busca de associação por id em tags pré-computadas.

## Detalhes por componente/área

### Origem das tags (pré-computadas)
- Índice da coluna: `SEQ_FAMOSA = 7` (`main.py:36`).
- Carga: `musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")` (`main.py:91`). Valores podem vir como strings com `NA` já tratado anteriormente (`line.replace('NA','')` em `main.py:75`).
- Passagem ao objeto: `Musica(..., musica[SEQ_FAMOSA], musica[TOM], musica[CIFRA])` (`main.py:103-106`).
- Armazenamento: `self.seqs_famosas = seqs_famosas` (`musica.py:22`).

### Mapeamento e busca
- Mapa hardcoded: `sequencias = {'BmGDA':0,'CGAmF':1,'EmG':2,'CA7DmG7':3,'GmF':4,'CC7FFm':5}` (`main.py:40-45`).
- `/similares` com `sequencia_tag`: `acordes = sequencia_tag.replace(',','')` (concatena, remove vírgulas) (`main.py:240`); se chave existe em `sequencias`, `id_seq = sequencias[acordes]` (`main.py:243`); chama `get_similares_por_sequencia(id_seq, generos_key)` e pagina (`main.py:244-246`).
- `get_similares_por_sequencia(id_seq, generos_key)` (`main.py:249-273`): filtra coleção por gênero via `apply_filtro` (`main.py:254`); itera músicas e faz `if str(id_seq) in musica.seqs_famosas:` (`main.py:259`) - membro em lista de strings/valores pré-computados. Monta dict com `id_unico_musica`, `id_artista`, `id_musica`, `nome_artista`, `nome_musica`, `popularidade`, `acordes`, `genero`, `url` (`main.py:260-271`).

### Comportamento relacionado a "ordem/repetições/normalização"
- **Ordem**: não é verificada no código atual. A condição é apenas pertencimento (`in`) da string do id na lista `seqs_famosas`. Não há extração de subsequências da cifra, não há comparação de ordem, não há algoritmo de subsequência.
- **Repetições**: não há tratamento. `Musica.acordes` é `list(set(cifra))` (`musica.py:21`) - conjunto de acordes únicos da cifra (usado em `/similares` por interseção/diferença). Já `seqs_famosas` é a lista vinda do CSV tal como foi splitada (`main.py:91`), armazenada sem transformação em `Musica` (`musica.py:22`); a busca por sequência usa essa lista pré-computada, não recalcula a partir de `cifra` com contagem/repetições.
- **Normalização**: não há normalização de acordes (maiúsculas/minúsculas, variações) no fluxo de busca por sequência. O mapeamento é por chave exata no dict `sequencias` (`main.py:40-45`); a comparação é `str(id_seq) in musica.seqs_famosas` sem normalização. Também não há uso de `remover_combinantes` no caminho `/similares` com `sequencia_tag` (essa função é usada em `/search`, `main.py:155-188`).

## Conexões e fluxos de dados
1. CSV `data/top/dataset_final.csv` coluna 7 → `musica[SEQ_FAMOSA].split(';')` (`main.py:91`) → `Musica.seqs_famosas` (`musica.py:22`).
2. Requisição `/similares?sequencia=BmGDA` → sem vírgulas → lookup em `sequencias` → id numérico → `in` em `seqs_famosas` pré-computadas → resultado paginado.

## Resposta direta às perguntas
- **O que vai definir "a sequência X aparece na música Y"?** No código atual: a associação pré-computada. "Aparece" significa que o id numérico da sequência X (mapeado pelas 6 hardcoded) está presente na lista `SEQ_FAMOSA` da música tal como veio do CSV e foi armazenada em `Musica.seqs_famosas`. Não é uma detecção dinâmica a partir da cifra.
- **A ordem dos acordes importa?** Não no mecanismo atual - não há verificação de ordem; é teste de pertinência (`in`) em lista de ids pré-computados.
- **Repetições de acorde dentro da música importam?** Não no mecanismo atual para esta busca; `seqs_famosas` vem pré-computada do CSV e não é derivado em tempo real de `cifra` com contagem. Além disso, `Musica.acordes` descarta duplicados via `set(cifra)` (`musica.py:21`), mas esse campo não é usado na busca por `sequencia_tag`.
- **É preciso normalizar (maiúsculas/minúsculas, variações)?** No caminho atual não há normalização aplicada. A chave é buscada exatamente como concatenada (após apenas remover vírgulas) no dict `sequencias` (`main.py:40,240,243`); a comparação com tags é `str(id_seq) in musica.seqs_famosas` sem normalização.
