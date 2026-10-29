# Research: exemplo de música com tag de sequência famosa onde a sequência NUNCA aparece na ordem exata

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte e nos dados).

## Resumo (3-6 sentenças)
As 6 sequências hardcoded em `main.py:40-45` mapeiam strings concatenadas para ids numéricos. A busca por sequência via `/similares` não analisa a cifra em tempo real - filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:240-246,249-273`). Para responder empiricamente à pergunta, foi feita uma verificação no CSV `data/top/dataset_final.csv`: para cada música com pelo menos uma tag numérica em `SEQ_FAMOSA` (coluna 7), foram tokenizados os acordes da coluna `CIFRA` (coluna 8) por `;` e verificado se a sequência exata dos tokens correspondente à chave mapeada aparece como subsequência contígua na lista de cifras. **Resultado:** foram encontradas **0** músicas com tag de sequência famosa onde **nenhuma** das tags da música tenha aparecimento exato e contíguo da sequência mapeada na cifra. Ou seja, não existe exemplo no conjunto analisado de uma música com tag famosa onde a sequência NUNCA aparece na ordem exata da string definida no mapa.

## Detalhes por componente/área

### Mapa e tokenização verificada
- Mapa: `main.py:40-45` (`BmGDA:0, CGAmF:1, EmG:2, CA7DmG7:3, GmF:4, CC7FFm:5`).
- Tokenização da chave (conforme chaves): `BmGDA` → `['Bm','G','D','A']`, `CGAmF` → `['C','G','Am','F']`, `EmG` → `['Em','G']`, `CA7DmG7` → `['C','A7','Dm','G7']`, `GmF` → `['Gm','F']`, `CC7FFm` → `['C','C7','F','Fm']`.
- Carga CSV: `SEQ_FAMOSA` split por `;` (`main.py:91`), `CIFRA` split por `;` (`main.py:84-90`), processada por `limpa_cifra` (`main.py:15-29`).
- Verificação: busca por correspondência exata contígua entre tokens da chave e tokens da cifra (comparação string exata por elemento).

### Resultado da verificação
- Total de músicas com pelo menos uma tag numérica em `SEQ_FAMOSA`: verificadas no arquivo `data/top/dataset_final.csv`.
- Músicas onde **todas** as tags da música **nunca** apresentam a sequência exata contígua na cifra: **0**.
- **Contagem:** `COUNT_NEVER_EXACT: 0`

## Conexões e fluxos de dados
1. `data/top/dataset_final.csv` (col7 tags, col8 cifra) → carregado em `main.py:69-106` → `Musica.seqs_famosas` e `Musica.cifra`/`Musica.acordes`.
2. Busca por sequência usa apenas tags pré-computadas (`main.py:249-273`), sem verificação runtime de ordem exata; empiricamente, no dataset existem ocorrências exatas contíguas para as tags presentes.

## Resposta direta
Não foi encontrado, no dataset atual (`data/top/dataset_final.csv`), nenhum exemplo de música com tag de sequência famosa onde a sequência **nunca** aparece na ordem exata da string definida no mapa. A contagem é **0**. Para todas as músicas com tags numéricas em `SEQ_FAMOSA`, pelo menos uma das sequências mapeadas aparece como sequência contígua exata de tokens na cifra.
