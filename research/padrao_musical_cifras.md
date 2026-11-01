# Research: padrão musical das cifras

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte e nos dados).

## Resumo (3-6 sentenças)
Não há evidência, no código-fonte, de que todas as cifras sigam o mesmo padrão musical/notação. `limpa_cifra` (`main.py:15-29`) apenas filtra tablaturas (quando há `|`) e divide por espaços, sem parsear, normalizar ou padronizar acordes. Os tokens são preservados exatamente como aparecem após esse tratamento e armazenados em `Musica.cifra` (`musica.py:20`), com `Musica.acordes = list(set(cifra))` mantendo os mesmos tokens (`musica.py:21`). No dataset existem notações distintas coexistindo (ex. `maj7` vs `7M`, `+`, `add9`, inversões com `/`, acordes com `#`/`b`, extensões variadas), sem qualquer mecanismo no código para unificar essas variações.

## Detalhes por componente/área

### Tratamento no código
- `limpa_cifra` (`main.py:15-29`): não converte case, não mapeia enarmonias, não normaliza extensões, não canonicaliza inversões. Apenas extrai primeiro token antes de `|` (quando há tablatura) ou divide por espaços e concatena tokens.
- Carga: `musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))` (`main.py:84-90`). `Musica` armazena `self.cifra = cifra` e `self.acordes = list(set(cifra))` (`musica.py:18-21`).
- Sem normalização aplicada a cifras em nenhum fluxo analisado (ver `research/normalizacao_cifras.md`).

### Exemplos de variações no mesmo dataset
Amostragem de `data/top/dataset_final.csv` (após limpeza por `limpa_cifra`):

- `14-bis/eu-ja-fechei-meu-olhos`: `['Cmaj7', 'Em7', 'Cadd9', 'C', 'Bm7', 'C', 'Em', 'C', 'Bm7', 'Am7']` - usa `maj7` e `add9`.
- `14-bis/dou-minha-palavra`: `['Eadd9', 'C#m7', 'Aadd9', 'F#m', 'B', 'G#/C', 'C#m7', 'Am/C', 'E/B', 'F#m']` - usa `add9`, sustenidos (`#`), inversões com barra (`/C`, `/C`, `/B`).
- `14-bis/cinema-de-faroeste`: `['Am', 'Am7', 'Am6', 'F7M/A', 'Am', ...]` - usa `6`, `7M` e inversão `F7M/A`.
- `14-bis/espanhola`: `['C7+', 'D/C', 'Bm7', 'Em7/9', 'Am7', 'D9/F#', 'G7/4', 'G', ...]` - usa `+`, `7/4`, inversão com `F#`.
- `14-bis/adoraveis-criaturas`: `['Bb9', 'C9', 'Dm4/7', 'Bb9', ..., 'Am7', 'D', ...]` - usa `9`, `4/7`, bemol (`Bb`).
- `14-bis/cancao-da-america`: `['Dm', 'G', 'C', 'F', 'G', 'F', 'C', 'Dm', 'G', 'Am']` - forma mais simples (`m` sem extensões).

Essas formas distintas coexistem no mesmo dataset sem conversão entre elas pelo código.

## Conexões e fluxos de dados
1. `data/top/dataset_final.csv` coluna CIFRA → `main.py:84-90` (split `;` + `limpa_cifra`) → tokens preservados → `Musica.cifra` e `Musica.acordes` (`musica.py:18-21`).
2. Uso posterior: `Musica.acordes` (distintos, tokens originais) usado em interseção/diferença em `/similares` (`main.py:303-349`); `Musica.cifra` completa armazenada mas não normalizada.

## Resposta direta
**Não, necessariamente.** O código não impõe um padrão único - ele apenas tokeniza. No dataset atual coexistem diferentes notações musicais (ex. `maj7` vs `7M`, `add9`, `+`, `7/4`, inversões `/X`, `#`/`b`, diferentes extensões) sem padronização. Todas são tratadas como tokens distintos pelo código (`Musica.acordes = set(cifra)`, buscas por interseção/comparação usam esses tokens tal como estão).
