# Research: padrão de maiúsculas/minúsculas nas cifras após limpeza

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte e nos dados).

## Resumo (3-6 sentenças)
Após a limpeza feita por `limpa_cifra` (`main.py:15-29`), **nem todas as cifras seguem o mesmo padrão de apenas maiúsculas**. Há acordes com letras minúsculas como `m`, `b`, `add`, `maj`, etc. (ex. `Am`, `Dm`, `Bm`, `Em`, `F#m`, `C#m`, `Am7`, `Bm7`, `Em7`, `Cadd9`, `Cmaj7`) e também símbolos como `#`, `/` para inversões/bass (ex. `D/C`, `F/D`, `C/E`, `G#/C`) e números/símbolos adicionais (`7`, `9`, `7M`, `7/4`, `4(7/9)`, `add9`, `maj7`, `+`). As raízes podem vir em maiúsculas ou, em casos com bemol/sustenido, a raiz é a letra com acidente (ex. `Bb`, `F#`). Não há conversão para maiúsculas/minúsculas no código - os tokens são preservados como aparecem (após filtrar tablaturas e dividir por espaços).

## Detalhes por componente/área

### Comportamento da limpeza
- `limpa_cifra` (`main.py:15-29`): não aplica `.upper()` nem `.lower()`. Para elementos sem `|`, faz `tokens = [token for token in m.split()]; cifra += tokens`. Para elementos com `|`, extrai `acorde = m.split('|')[0].split()[0]`. Preserva o token original.
- Carga: `musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))` (`main.py:84-90`).

### Exemplos observados (após limpeza)
- `14-bis/adoraveis-criaturas`: `['Bb9', 'C9', 'Dm4/7', 'Bb9', ..., 'Am7', 'D', ...]` - mistura `Bb`, `Dm`, `Am` (minúsculo `m`).
- `14-bis/ate-o-dia-clarear`: `['G', 'Am7', 'D/C', 'Bm7', 'Em7', 'A7/4', ...]` - `Am7`, `Bm7`, `Em7`, inversões `/C`.
- `14-bis/cancao-da-america`: `['Dm', 'G', 'C', 'F', ..., 'Am', ...]`
- `14-bis/cinema-de-faroeste`: `['Am', 'Am7', 'Am6', 'F7M/A', ...]` - `F7M/A` com `7M` e inversão.
- `14-bis/eu-ja-fechei-meu-olhos`: `['Cmaj7', 'Em7', 'Cadd9', 'C', 'Bm7', ...]` - `maj7`, `add9`.
- `14-bis/dou-minha-palavra`: `['Eadd9', 'C#m7', 'Aadd9', 'F#m', 'B', 'G#/C', ...]` - `#`, inversão.
- `14-bis/espanhola`: `['C7+', 'D/C', 'Bm7', 'Em7/9', 'Am7', 'D9/F#', ...]` - `+`, `/F#`.

## Conexões e fluxos de dados
- CSV coluna CIFRA → split por `;` → `limpa_cifra` (sem alteração de case) → `Musica.cifra` (`main.py:84-90`, `musica.py:20`).
- `Musica.acordes = list(set(cifra))` preserva os tokens como estão (`musica.py:21`).

## Resposta direta
**Não.** Após a limpeza, as cifras não seguem um padrão apenas em maiúsculas. Há letras minúsculas para indicar menor/menor com extensões (`m`, `m7`), bemóis/sustenidos (`b`, `#`), notações como `add`, `maj`, `+`, bem como inversões com barra (`/C`, `/F#`) e números extensos. O código não normaliza maiúsculas/minúsculas - os acordes são mantidos exatamente como aparecem após filtrar tablaturas e dividir por espaços.
