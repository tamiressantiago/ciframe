# Research: sequências por música (tag), ordem, repetições e exemplos do CSV

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte).

## Resumo (3-6 sentenças)
As tags `SEQ_FAMOSA` vêm pré-computadas da coluna 7 do CSV `data/top/dataset_final.csv` (`main.py:36,91`), splitadas por `;` e armazenadas em `Musica.seqs_famosas` (`musica.py:22`). No caminho atual, a busca por sequência via `/similares?sequencia=...` não analisa a cifra - mapeia a string concatenada (sem vírgulas) para um id numérico pelo dict `sequencias` (`main.py:40-45,240-246`) e filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:249-273`). Com base em exemplos reais do CSV, a ordem da sequência na tag não é "reconstruída" em tempo real; trata-se de associação por id pré-computado. A cifra é armazenada como lista de tokens separados por `;` no CSV, carregada tal como splitada após `limpa_cifra` sobre split por `;` (`main.py:84-90`), e `Musica.acordes` é `list(set(cifra))` (distintos) (`musica.py:21`), enquanto a sequência tag é distinta do conjunto de acordes distintos.

## Exemplos concretos do CSV (linhas reais)

### Exemplo 1: id_seq 0 (mapa `BmGDA`/`...` para 0)
- Linha (aprox): `30-seconds-to-mars,city-of-angels,...,Alternativo,16307,D,0,D;A;Bm;G;D;A;Bm;G;...`  
  Arquivo: `data/top/dataset_final.csv:135` (1-based no grep acima; verificado por amostragem)
  - Colunas (split por `,` conforme carregamento): ARTISTA_ID=`30-seconds-to-mars`, MUSICA_ID=`city-of-angels`, ARTISTA=`30 Seconds To Mars`, MUSICA=`City Of Angels`, GENERO=`Alternativo`, POPULARIDADE=`16307`, TOM=`D`, SEQ_FAMOSA=`0`, CIFRA=`D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;G;D;A;Bm;G;A;G;D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;A;G`
- Carga: `musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")` → `['0']` (`main.py:91`); `musica[CIFRA]` split por `;` → lista passada a `limpa_cifra` (`main.py:84-90`).
- No `Musica`: `seqs_famosas = ['0']` (`musica.py:22`), `acordes = list(set(cifra))` → distintos da cifra (ordem em set não preservada; convertido para lista). A cifra original nesta música mostra repetições sequenciais: começa `D;A;Bm;G;D;A;Bm;G;...` com blocos repetidos e depois repetições adicionais (inclui `G;D;A;Bm;G;A;G;...`).

### Exemplo 2: id_seq 1
- `5-seconds-of-summer/bad-dreams` (Pop Rock), SEQ_FAMOSA=`1`, CIFRA começa `C;F;Am;G;C;C;F;F;C;...` (`data/top/dataset_final.csv` linha ~204 conforme amostragem).  
- `5-seconds-of-summer/broken-pieces` SEQ_FAMOSA=`1`, CIFRA começa `C;G;Am;F;C;G;Am;F;...`  
- `5-seconds-of-summer/fly-away` SEQ_FAMOSA=`1`, CIFRA começa `C;G;Am;F;C;G;Am;F;...`  
- `5-seconds-of-summer/heartache-on-the-big-screen` SEQ_FAMOSA=`0`, CIFRA começa `D;G;D;G;D;G;D;G;D;G;D;A;G;D;Bm;G;...`

## Ordem na música vs ordem na sequência (observado)
- **No mecanismo atual**: não há comparação entre ordem da cifra e ordem da sequência. A "aparição" é por associação pré-computada (tag). O código não extrai subsequências da lista `cifra` nem verifica posições/ordem - apenas testa `str(id_seq) in musica.seqs_famosas` (`main.py:259`).
- **No CSV**: a tag é um id numérico (ex. `0`, `1`) - não é a string da sequência concatenada. A relação entre qual sequência corresponde a qual id é definida apenas pelo mapa hardcoded `sequencias` em `main.py:40-45`. Não há, no código, informação sobre "ordem que aparece na música" derivada em tempo real; essa informação, se existir, estaria apenas nas tags pré-computadas do próprio CSV (fora do escopo do código analisado).

## Acordes repetidos / sequenciais / distintos
- **Cifra carregada**: `musica[CIFRA]` recebe a lista de tokens da cifra (após `limpa_cifra` sobre split por `;` em `main.py:84-90`). `limpa_cifra` filtra tabs por `|` pegando primeiro token antes de `|`, senão divide por espaços e concatena tokens (`main.py:15-29`).
- **Distintos vs totais**: `Musica.acordes = list(set(cifra))` (`musica.py:21`) - guarda **apenas acordes distintos** (conjunto). Em contraste, a lista `cifra` completa (com repetições e ordem) fica em `self.cifra = cifra` (`musica.py:20`).
- **Repetições sequenciais**: observados nos exemplos acima (ex. `C;C;F;F;C;...` em *Bad Dreams*, blocos repetidos em *City Of Angels*). O código não remove repetições da `cifra` completa; `set()` é aplicado apenas para construir `self.acordes`.
- **Uso**: `Musica.acordes` (distintos) é usado em `/similares` por interseção/diferença (`main.py:303-349`). A lista `self.cifra` completa permanece armazenada mas, nos fluxos analisados, não é usada para busca por sequência ou para cálculo de similaridade por sequência.

## Como acorde e cifra são guardados no CSV (2 exemplos)
**Exemplo A (acorde individual / forma na cifra):**
- Na linha de `30-seconds-to-mars/city-of-angels` (`data/top/dataset_final.csv`), coluna CIFRA (índice 8): começa com `D;A;Bm;G;D;A;Bm;G;...`  
  - Cada elemento entre `;` é um token de acorde conforme aparece na cifra (ex. `D`, `A`, `Bm`, `G`).  
  - No carregamento: split por `;` → lista de strings; `limpa_cifra` processa cada elemento (se contém `|` pega primeiro token antes de `|` e antes de espaço, senão divide por espaços e concatena) (`main.py:15-29,84-88`).  
  - Armazenado como `self.cifra` (lista) e `self.acordes` (conjunto de distintos) em `Musica` (`musica.py:18-21`).

**Exemplo B (com alterações/variações):**
- Na mesma linha, aparecem tokens como `Bm`, `G`, `D` etc., também `A` simples. Em outra amostra, `5-seconds-of-summer/bad-dreams` tem `Am`, `F`, `G`, `C` e repetições (`C;C;F;F;...`).  
  - Formato no CSV: string da coluna CIFRA com elementos separados por `;` (sem aspas na amostra), podendo conter acordes com letras/números/símbolos como aparecem (ex. `Bm`, `Am`, `D`, `G`, `C`).  
  - Tratamento: `limpa_cifra` não normaliza maiúsculas/minúsculas nem mapeia variações - apenas filtra tablaturas e divide por espaços (`main.py:15-29`). Não há transformação para forma canônica no código-fonte atual.

## Conexões e fluxos de dados
1. `data/top/dataset_final.csv` colunas 7 (SEQ_FAMOSA), 8 (CIFRA) → `main.py:75-91` → split `;` para SEQ_FAMOSA e CIFRA → `limpa_cifra` → `Musica` (`musica.py:5-22`).
2. Busca por sequência → mapeamento hardcoded `sequencias` → id → filtro por tag pré-computada (sem análise de ordem/repetições/normalização da cifra).
