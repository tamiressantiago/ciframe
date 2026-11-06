# Research: página `#/porsequencia` (sequencia.html + sequencia.js)

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte).

## Resumo (3-6 sentenças)
A rota `#/porsequencia` usa o template `static/templates/sequencia.html` e o controller `static/assets/js/controllers/sequencia.js`. Atualmente exibe 4 sequências hardcoded (BmGDA, CGAmF, GmF, CC7FFm), ao clicar chama `vm.pesquisarPorSequencia(sequencia)` montando `similares?sequencia=<acordes separados por vírgula>` e faz GET para o backend. O backend (`main.py:225-247`) concatena sem vírgulas, mapeia a string no dicionário `sequencias` (`main.py:40-45`) para `id_seq` numérico e chama `get_similares_por_sequencia(id_seq, generos_key)` que filtra por gênero e retorna músicas com `str(id_seq)` em `musica.seqs_famosas` (`main.py:249-273`). Não há verificação de ordem consecutiva exata nem filtro "apenas acordes da sequência" no frontend ou backend - trata-se de busca por tag pré-computada.

## Detalhes por componente/área

### Template
- Arquivo: `static/templates/sequencia.html`
- Exibe 4 blocos de acordes via `ng-repeat='sequencia in Sequencia.sequenciasFamosas'` com `ng-click="Sequencia.pesquisarPorSequencia(sequencia)"` (linhas ~5-7).
- Ao ter `Sequencia.minhaSequencia.acordes.length`, mostra seletor de gênero (`Sequencia.generos`) com `ng-change="Sequencia.pesquisarPorSequencia()"` e os acordes da sequência clicada (linhas ~25-49).
- Lista resultados em cards (`ng-repeat="music in Sequencia.musics"`) com `ng-click="Sequencia.goToLirics(music)"` abrindo `music.url` (linhas ~53-75).
- Botão "Encontrei essas músicas" chama `Sequencia.goToResults()` fazendo scroll até `#results` (linhas ~10-14).

### Controller
- Arquivo: `static/assets/js/controllers/sequencia.js`
- Sequências hardcoded:
  - `sequencia1`: Bm, G, D, A (`index:1`)
  - `sequencia2`: C, G, Am, F
  - `sequencia3`: Gm, F
  - `sequencia4`: C, C7, F, Fm
- Push em `vm.sequenciasFamosas` (linhas ~49-52).
- `createChordsString(chords)`: concatena `chords[i].acorde + ','` e remove última vírgula (linhas ~73-78).
- `vm.pesquisarPorSequencia(sequencia)`: se recebida, seta `vm.minhaSequencia = sequencia`; monta `searchString = "similares?sequencia=".concat(createChordsString(...))`; adiciona `&generos=...` se selecionado; faz `$http.get(apiUrl.concat(searchString))`. Em sucesso seta `vm.musics = data`, exibe contagem; em erro limpa flags (linhas ~80-115).
- `vm.limparPesquisa()`: zera `vm.minhaSequencia` e `vm.musics` (linhas ~117-120).
- `vm.goToLirics(music)`: `$window.open(music.url)` (linha ~122-124).
- `vm.goToResults()`: scroll até `#results` (linhas ~126-129).

### Backend (fluxo acionado)
- Rota: `main.py:225-247` (`/similares`)
  - Lê `sequencia_tag`, `generos_tag`, `pagina_tag`.
  - Se `sequencia_tag`: `acordes = sequencia_tag.replace(',','')` (concatena); se em `sequencias` (`main.py:40-45`), obtém `id_seq`; chama `get_similares_por_sequencia(id_seq, generos_key)` e retorna paginado.
- `get_similares_por_sequencia(id_seq, generos_key)`: `main.py:249-273` filtra por gênero via `apply_filtro`, seleciona músicas onde `str(id_seq) in musica.seqs_famosas`, retorna lista com campos incluindo `acordes`, `popularidade`, `genero`, `url`.
- Músicas carregadas de `data/top/dataset_final.csv`: `SEQ_FAMOSA` split por `;` → `Musica.seqs_famosas` (`main.py:91`, `musica.py:22`).

## Conexões e fluxos de dados
1. Clique em sequência hardcoded → `sequencia.js` monta query `similares?sequencia=A,B,...`
2. `main.py` remove vírgulas → lookup em `sequencias` → id numérico → busca em `seqs_famosas` pré-computadas → retorna músicas
3. Frontend exibe resultados em cards

## O que faz hoje (resumido)
Exibe 4 sequências famosas hardcoded, permite filtrar por gênero, consulta `/similares?sequencia=...` e mostra as músicas retornadas pelo backend com base em **tags pré-computadas** `SEQ_FAMOSA` mapeadas pelos ids das 6 sequências hardcoded. Não implementa busca por "apenas acordes da sequência" nem por ocorrência consecutiva exata da cifra - essa lógica não existe nesta página/código atual.
