# Research: acordes fora da sequência famosa nas músicas com tag

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte e nos dados).

## Resumo (3-6 sentenças)
Foram revisadas todas as músicas com tag de `SEQ_FAMOSA` no `data/top/dataset_final.csv` (coluna 7). Para cada música com tag numérica, foram considerados os acordes distintos da cifra (tokens após split por `;`, tal como carregados) e comparados com o conjunto de acordes distintos presentes nas sequências mapeadas pelas tags da música (mapeamento em `main.py:40-45`). Não há normalização aplicada (conforme código). **Resultado:** de **514** músicas com tag de sequência famosa, **0** apresentam acordes distintos fora dos presentes na(s) sequência(s) famosa(s) da música. Todas as 514 têm apenas acordes que pertencem ao conjunto de acordes das sequências mapeadas por suas tags.

## Detalhes por componente/área

### Mapeamento e verificação
- Mapa hardcoded: `main.py:40-45` (`BmGDA:0, CGAmF:1, EmG:2, CA7DmG7:3, GmF:4, CC7FFm:5`).
- Tokenização das chaves: `BmGDA`→`['Bm','G','D','A']`, `CGAmF`→`['C','G','Am','F']`, `EmG`→`['Em','G']`, `CA7DmG7`→`['C','A7','Dm','G7']`, `GmF`→`['Gm','F']`, `CC7FFm`→`['C','C7','F','Fm']`.
- Carga: `SEQ_FAMOSA` split por `;` (`main.py:91`), `CIFRA` split por `;` (`main.py:84-90`), sem normalização (`limpa_cifra` apenas filtra tablaturas e divide por espaços, `main.py:15-29`).
- Comparação: para cada música com tag(s), união dos acordes distintos das sequências mapeadas vs acordes distintos da cifra (tokens exatos). Diferença = acordes na cifra não presentes na sequência.

### Resultado
- `TOTAL_MUSICAS_COM_TAG`: 514
- `COM_ACORDES_FORA_DA_SEQUENCIA`: 0
- `SEM_ACORDES_FORA_DA_SEQUENCIA`: 514

**Ocorrências com acordes diferentes dos presentes da sequência:** 0.

## Conexões e fluxos de dados
1. `data/top/dataset_final.csv` col7 (SEQ_FAMOSA) e col8 (CIFRA) → carregamento conforme `main.py:69-106` → comparação por conjuntos de tokens distintos (sem normalização).

## Resposta direta
Em **todas** as 514 músicas com tag de sequência famosa, a cifra apresenta **apenas** acordes presentes na(s) sequência(s) famosa(s) mapeada(s) por suas tags. Não foram encontradas ocorrências com acordes diferentes dos presentes na sequência - **0 ocorrências**.
