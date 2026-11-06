# Research: padrão entre cifra no CSV e sequência famosa (análise observacional)

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte).

Mapeamento de ids (hardcoded em `main.py:40-45`): `BmGDA:0, CGAmF:1, EmG:2, CA7DmG7:3, GmF:4, CC7FFm:5`.

## Resumo (3-6 sentenças)
As tags `SEQ_FAMOSA` (`data/top/dataset_final.csv`, col 7) são pré-computadas e armazenadas em `Musica.seqs_famosas` (`main.py:91`, `musica.py:22`). No mecanismo atual, `/similares?sequencia=...` não analisa a cifra em tempo real - mapeia a string concatenada (sem vírgulas) para id numérico e filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:40-45,240-246,249-273`). A análise empírica das cifras mostra: (1) nem sempre a sequência aparece na ordem exata da cifra em todas as músicas com aquela tag; (2) há músicas com a tag onde a ordem exata da sequência aparece em trechos, mas também há variações/ordens diferentes em outras posições; (3) existem cifras com acordes repetidos consecutivamente (ex. `C;C;F;F;...`, blocos repetidos) e, nessas, o aparecimento da sequência "normal" (sem repetições) pode ocorrer ou não conforme os trechos - não é regra geral observada.

## 1) A ordem que aparece na música é a mesma que aparece na sequência?

**Sequência CGAmF (id 1):** chave concatenada `C,G,Am,F`.

Exemplos observados no CSV:

- `5-seconds-of-summer/broken-pieces` (seqs `1`), CIFRA começa: `C;G;Am;F;C;G;Am;F;C;G;Am;F;...`  
  - Aparece em ordem exata `C,G,Am,F` em blocos consecutivos desde o início.
- `5-seconds-of-summer/fly-away` (seqs `1`), começa: `C;G;Am;F;C;G;Am;F;...` - ordem exata em blocos.
- `5-seconds-of-summer/lost-boy` (seqs `1`), começa: `C;G;Am;F;C;G;Am;F;...` - ordem exata em blocos.
- `5-seconds-of-summer/bad-dreams` (seqs `1`), CIFRA começa: `C;F;Am;G;C;C;F;F;C;C;F;F;G;F;G;F;C;G;Am;F;...`  
  - No início: `C,F,Am,G,...` que **não** é `C,G,Am,F`. Mais adiante aparece `C;G;Am;F` (ex. `...;C;G;Am;F;C;G;Am;F;G;C;...`) - ou seja, **há trechos em ordem diferente no início e trechos em ordem exata `C,G,Am,F` em outras posições**.
- `5-seconds-of-summer/the-only-reason` (seqs `1`), começa: `C;G;Am;F;F;C;G;Am;F;...` - começa em ordem exata, com repetições.
- `5-seconds-of-summer/wherever-you-are` (seqs `1`), começa: `C;Am;F;C;G;Am;F;C;G;Am;F;...` - início com `C,Am,F,...` (diferente), depois aparece `C;G;Am;F`.
- `alan-jackson/little-man` (seqs `1`), começa: `C;F;C;G;F;C;G;F;...` - não começa em `C,G,Am,F`.
- `banda-calypso/primeiro-amor` (seqs `1`), começa: `Am;F;C;G;Am;F;C;G;...` - começa em ordem diferente (`Am,F,C,G`).
- `avril-lavigne/i-can-do-better` (seqs `1`), começa: `C;G;F;C;G;F;...` - diferente.
- `birdy/not-about-angels` (seqs `1`), começa: `Am;Am;F;C;Am;F;C;...` - diferente.

**Sequência BmGDA (id 0):** chave concatenada `B,m,G,D,A`? Mapa `main.py:40-45`: `BmGDA' : 0` (string concatenada).  
Exemplos:
- `30-seconds-to-mars/city-of-angels` (seqs `0`), CIFRA começa: `D;A;Bm;G;D;A;Bm;G;D;A;Bm;G;...` - começa com `D,A,Bm,G,...` (ordem diferente da chave concatenada `BmGDA` tal como escrita). Aparece em bloco `D;A;Bm;G` repetidamente; a chave `BmGDA` não aparece como sequência iniciando na ordem da chave no início.
- `5-seconds-of-summer/heartache-on-the-big-screen` (seqs `0`), começa: `D;G;D;G;D;G;...` com repetições, depois aparece `D;A;G;D;Bm;G;...` (ordem diferente).

**Conclusão observacional:** **Não em todas as vezes a sequência aparece na cifra na ordem exata da sequência mapeada.** Há casos onde aparece em ordem exata em blocos (ex. *broken-pieces*, *fly-away* com `C,G,Am,F`), mas também há casos com a mesma tag onde a ordem exata não aparece no início ou aparece em ordens diferentes em diferentes trechos (*bad-dreams* tem trechos diferentes; *wherever-you-are* tem início diferente; muitas músicas em tonalidade/forma diferentes começam com outros acordes). A tag é pré-computada (associação), não verificada em tempo real pelo código.

## 2) Na música, temos acordes repetidos ou apenas distintos?

- **Cifra completa** (`self.cifra`, `main.py:90`, `musica.py:20`): contém repetições e ordem tal como processada.  
- **Acordes distintos** (`self.acordes = list(set(cifra))`, `musica.py:21`): apenas distintos. Usado em `/similares` por interseção (`main.py:303-349`).
- **Observação empírica:** Muitas cifras têm repetições. Exemplo claro: `5-seconds-of-summer/bad-dreams` começa `C;F;Am;G;C;C;F;F;C;...` (repetições consecutivas `C;C`, `F;F`). `5-seconds-of-summer/the-only-reason` tem `F;F`, `C;G;Am;F;Am;F;...`, `G;G;G;F;...`. `30-seconds-to-mars/city-of-angels` tem repetições de blocos `D;A;Bm;G` e depois `G;D;A;Bm;G;...`. Há também músicas com repetições longas (ex. *bon-jovi/amen* tem muitos blocos repetidos, *birdy/terrible-love* começa com repetições).

## 3) Se houver repetidos, um mesmo acorde aparece em posições sequenciais?

Sim, observado em vários exemplos:
- `5-seconds-of-summer/bad-dreams`: `C;C;F;F;C;C;F;F;G;F;G;F;...` - `C` aparece consecutivamente, `F` consecutivamente.
- `5-seconds-of-summer/the-only-reason`: `C;G;Am;F;F;C;G;Am;F;...` - `F;F` consecutivo; depois `Am;F;Am;F;...`, `G;G;G;F;...`.
- `30-seconds-to-mars/city-of-angels`: blocos inteiros repetidos sequencialmente (ex. `D;A;Bm;G;D;A;Bm;G;...` aparece múltiplas vezes).
- `avril-lavigne/i-can-do-better`: repetições como `C;G;F;C;G;F;...` com repetições de blocos.
- `birdy/terrible-love`: começa com `C;F;C;F;C;F;...` (alternando/repetindo blocos em sequência).

## 4) Existe alguma música que os acordes vem sempre repetidos? Exemplo CCGGAmAmFF?
Não há evidência de que "sempre" venham repetidos em todas as posições - é comum haver blocos com repetições consecutivas e blocos sem repetições. Exemplos com repetições consecutivas de mesmo acorde:
- `5-seconds-of-summer/bad-dreams`: `C;C;F;F;C;C;F;F;...` (sim, repetições consecutivas de `C` e `F`).
- `5-seconds-of-summer/the-only-reason`: `F;F` (consecutivos), `G;G;G` (consecutivos).
- `bryan-adams/i-will-be-right-here`: tem repetições em blocos.
- `birdy/terrible-love`: repetições alternadas/blocos com repetições.

Não foi observado um padrão uniforme "CCGGAmAmFF" ao longo de toda a música em amostras - o mais comum são repetições pontuais/consecutivas ou repetições de blocos inteiros.

## 5) Nessas músicas a sequência normal (sem repetir o acorde) também aparece?
Sim, nos exemplos com repetições consecutivas também aparecem ocorrências da sequência "normal" (sem repetições).
- `5-seconds-of-summer/bad-dreams` (tag 1 = `CGAmF`): tem `C;C;F;F;...` no início e também aparece `C;G;Am;F` mais adiante (`...;C;G;Am;F;C;G;Am;F;G;C;...`).
- `5-seconds-of-summer/the-only-reason` (tag 1): começa `C;G;Am;F;F;...` (tem `F;F` mas também começa com `C,G,Am,F` sem repetir os 4 seguidos). Mais adiante aparecem variações.
- `30-seconds-to-mars/city-of-angels` (tag 0): repetições de bloco `D;A;Bm;G` aparecem como bloco sem repetições consecutivas internas além da repetição do próprio bloco.
- `birdy/terrible-love` (tag 1): começa com `C;F;C;F;...` (repetições de pares) e também tem seções com `C;G;Am;F`? Na amostra: começa `C;F;C;F;C;F;...` alternando, mais adiante aparece `Am;F;C;G;Am;F;C;G;...` (aparece `C;G;Am;F` em ordem invertida em relação ao padrão `C,G,Am,F`? `C;G;Am;F` seria C,G,Am,F; em `Am;F;C;G;Am;F;C;G` temos Am,F,C,G - ordem diferente).

## Exemplos concretos exibidos
1. **Ordem exata presente**: `5-seconds-of-summer/broken-pieces` (CSV linha ~206) - `C;G;Am;F;C;G;Am;F;...` tag `1` (CGAmF) - ordem exata aparece desde o início.
2. **Ordem diferente + ordem exata em outro trecho**: `5-seconds-of-summer/bad-dreams` (CSV linha ~204) - tag `1`, início `C;F;Am;G;C;C;F;F;...` (diferente) mas aparece `C;G;Am;F` mais adiante.
3. **Repetições consecutivas**: `5-seconds-of-summer/bad-dreams` - `C;C;F;F;C;C;F;F;...`; `5-seconds-of-summer/the-only-reason` - `F;F`, `G;G;G`.
4. **Música com tag mas início diferente**: `banda-calypso/primeiro-amor` tag `1`, começa `Am;F;C;G;Am;F;C;G;...` (ordem diferente), `avril-lavigne/i-can-do-better` começa `C;G;F;C;G;F;...`.

## Conexões e fluxos de dados (relevantes)
- Carga: `data/top/dataset_final.csv` col7 `SEQ_FAMOSA` split por `;` → `main.py:91` → `Musica.seqs_famosas` (`musica.py:22`).
- Busca por sequência: mapa `sequencias` (`main.py:40-45`) → id → `get_similares_por_sequencia` filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:249-273`) - **sem análise de ordem/repetições/normalização da cifra**.
- Cifra: split por `;` após `limpa_cifra` (`main.py:84-90`), `Musica.acordes = set(cifra)` (distintos) usado apenas em `/similares` por interseção (`main.py:21`, `main.py:303-349`).

## Observação final
A relação observada é: **muitas músicas com tag de sequência famosa possuem trechos onde a sequência aparece na ordem exata "normal" (sem repetições consecutivas internas), mas nem todas as músicas com aquela tag apresentam a ordem exata no início ou em todas as posições - há variações de ordem e repetições consecutivas.** O código-fonte atual não realiza essa verificação em tempo real; a associação é pré-computada no CSV.
