# Research: normalização de cifras atualmente

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte).

## Resumo (3-6 sentenças)
Atualmente **não há normalização aplicada às cifras** no carregamento ou nos fluxos analisados. `limpa_cifra` (`main.py:15-29`) apenas filtra tablaturas (quando há `|` pega o primeiro token antes de `|` e espaço) e divide por espaços concatenando tokens; não converte maiúsculas/minúsculas, não mapeia variações de escrita de acordes, não remove repetições e não aplica normalização Unicode. A única normalização Unicode presente é `remover_combinantes` (`main.py:145-147`) usada exclusivamente em `/search` para busca textual (artista/música/keys) com `unicodedata.normalize('NFD', ...)` removendo marcas diacríticas (`main.py:118-130`); não é aplicada a `cifra`, `acordes`, `seqs_famosas` ou ao caminho `/similares`.

## Detalhes por componente/área

### Carregamento e tratamento da cifra
- Leitura: `musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))` se não vazia, senão `[]` (`main.py:84-90`).
- `limpa_cifra(raw_cifra)` (`main.py:15-29`):
  ```python
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
  ```
  - Apenas filtra tablaturas e divide por espaços. Sem `.lower()`, `.upper()`, sem mapeamento de variações (ex. `#`/`b`, equivalências), sem remoção de caracteres, sem normalização Unicode.

### Armazenamento
- `Musica.cifra = cifra` (lista completa com ordem e repetições) (`musica.py:20`).
- `Musica.acordes = list(set(cifra))` (apenas distintos; ordem não preservada) (`musica.py:21`).
- `Musica.seqs_famosas` vem de `SEQ_FAMOSA.split(';')` sem transformação (`main.py:91`, `musica.py:22`).

### Uso
- Busca por sequência (`/similares?sequencia=...`): mapeia string concatenada sem vírgulas para id via `sequencias` (`main.py:40-45,240-246`), filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:249-273`) - sem normalização.
- Similaridade por acordes (`/similares` sem `sequencia_tag`): usa `musica.acordes` (distintos) em interseção/diferença (`main.py:303-349`) - sem normalização.
- Busca textual (`/search`): aplica `.lower()` e `remover_combinantes` (NFD + remove marcas diacríticas) em keys e em `nome_artista/nome_musica` (`main.py:118-130,145-147`) - **único local com normalização**.

## Conexões e fluxos de dados
1. `data/top/dataset_final.csv` coluna CIFRA → `main.py:84-90` → `limpa_cifra` (sem normalização) → `Musica.cifra` / `Musica.acordes`.
2. `data/top/dataset_final.csv` coluna SEQ_FAMOSA → `main.py:91` → `Musica.seqs_famosas` (sem normalização).
3. Busca textual usa normalização Unicode+lowercase apenas para strings de texto (`/search`).

## Resposta direta
**Não.** Não há normalização de cifras atualmente. Não há conversão para maiúsculas/minúsculas, não há tratamento de variações de escrita do mesmo acorde (ex. enarmonias), não há normalização Unicode aplicada às cifras. Apenas `remover_combinantes` (NFD, remoção de diacríticos) é usado em `/search` para busca textual; nenhum tratamento similar é aplicado a `cifra`, `acordes` ou `seqs_famosas`.
