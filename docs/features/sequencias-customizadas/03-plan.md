# Plano — Sequências de Acordes Customizadas

## Passos

### 1. [x] Definir função de matching
- [x] **1.1** Analisar a regra em `docs/features/sequencias-customizadas/02-proposal.md`: (1) a música não pode ter acordes fora da sequência indicada; (2) a sequência deve aparecer na ordem exata e de forma sequencial ao menos uma vez (verificar nessa ordem).
- [x] **1.2** Criar função seguindo padrão existente no `main.py`. Sugestão de nome: `musica_tem_sequencia(musica, seq_tokens)` ou reutilizar lógica similar a `scripts/algoritmo.py:musica_contem_sequencia(cifra, seq_tokens)`. A função deve:
  - Usar `musica.cifra` (lista na ordem) após `limpa_cifra` (função em `main.py`) para verificar as duas regras: (1) o conjunto de acordes da cifra não pode ter acordes fora da sequência; (2) a sequência deve aparecer na ordem exata e de forma sequencial ao menos uma vez.
- [x] **1.3** Verificar com `scripts/algoritmo.py` e `artefatos/reppit/research/saida_validacao_matching.txt` que a lógica reproduz os matches das 6 originais. Não fazer normalização ampla das cifras.

### 2. [x] Criar banco SQLite e popular com as 6 sequências originais
- [x] **2.1** Usar `sqlite3` da stdlib. Usar caminho `data/db/` relativo à raiz do projeto (execução local a partir da raiz e `WORKDIR /app` no Docker), criando o diretório se não existir.
- [x] **2.2** Criar tabela `sequencias`:
  - `id` INTEGER PRIMARY KEY
  - `acordes` TEXT UNIQUE (acordes separados por espaço, ex.: `Bm G D A`)
- [x] **2.3** Na primeira execução (startup), popular com as 6 sequências originais definidas em `SEQUENCIAS_ORIGINAIS` (`main.py`) (inserir apenas se não existirem).
- [x] **2.4** Garantir que o arquivo seja gravado em `data/db/`, o mesmo caminho montado no volume do passo 6 (equivalente a `/app/data/db` no container).
- [x] **2.5** O banco não deve aceitar sequências repetidas (constraint `UNIQUE` em `acordes`).

### 3. [x] Atualizar .gitignore e .dockerignore para data/db/
- [x] **3.1** Adicionar `data/db/` em `.gitignore`.
- [x] **3.2** Adicionar `data/db/` em `.dockerignore`.

### 3.5 [x] Capturar baseline das 6 sequências (antes de alterar a busca)
- [x] **3.5.1** Antes de desligar o caminho por tag, capturar um baseline de `GET /similares` para cada uma das 6 sequências (lista de `id_unico_musica` na ordem, por página) e salvar em `tests/fixtures/similares_sequencias_baseline.json`, incluindo a ordem de gêneros usada (`generos_ordem`) para reproduzir a ordenação.

### 4. [x] Adicionar endpoints mencionados no 02-proposal.md
- [x] **4.1** **GET /sequencias** — lista unificada (6 originais + customizadas).
  - Ler com `sqlite3` em conexão por request: `SELECT id, acordes FROM sequencias ORDER BY id`.
  - Responder `json.dumps([{"id": 0, "acordes": "Bm G D A"}, ...])` (string, não `jsonify`; mantém o Content-Type legado).
  - `acordes` é texto canônico separado por espaço; ordem crescente de `id` (originais 0–5 primeiro).
  - Sem paginação (catálogo pequeno). Em erro de banco, responder 500 com `{"erro": "..."}`.
  - A rota explícita tem precedência sobre o catch-all `static_proxy`; confirmar que `GET /sequencias` não cai no arquivo estático.
- [x] **4.2** **POST /sequencias** — cadastro anônimo (sem login).
  - Aceitar JSON `{"acordes": "Am, F, C, G"}` via `request.get_json(silent=True)`; aceitar vírgula e/ou espaço como separador.
  - Criar helper `normalizar_sequencia(texto)` (reutilizado no 4.3): separar por vírgula/espaço, descartar tokens vazios, colapsar espaços, aplicar primeira letra maiúscula preservando o resto (`bm` → `Bm`, `c#m` → `C#m`, `cmaj7` → `Cmaj7`), preservar a ordem e juntar com espaço simples.
  - Validar: corpo ausente/inválido, `acordes` ausente/não-string ou normalização vazia → `400 {"erro": "..."}`.
  - Não validar tokens contra o conjunto de `/acordes` (decisão): acordes desconhecidos são aceitos e apenas não casam na busca.
  - Persistir com query parametrizada. `acordes` é `UNIQUE`; capturar `sqlite3.IntegrityError` e responder `409 {"erro": "sequencia ja existe", "id": <id>}` consultando o id existente.
  - Sucesso: `201 {"id": <novo_id>, "acordes": "<canonica>"}`; commit/rollback e fechar a conexão.
  - Conexões por request com `timeout`; não compartilhar conexão global entre threads/workers do gunicorn.
  - Segurança: endpoint público sem autenticação por escopo; queries parametrizadas.
- [x] **4.3** **Alterar `get_similares` (endpoint `GET /similares` em `main.py`)** — aceitar sequências originais ou customizadas.
  - Normalizar `sequencia_tag` com o mesmo `normalizar_sequencia` do 4.2 (aceitar `C,G,Am,F` e `C G Am F`).
  - Buscar no banco: `SELECT id FROM sequencias WHERE acordes = ?`. Se não existir, manter comportamento atual e retornar `json.dumps([])`.
  - Aplicar `musica_tem_sequencia` (passo 1) em tempo real para todas as sequências; não usar mais `SEQ_FAMOSA`/`seqs_famosas`. Se `get_similares_por_sequencia` ficar sem uso, remover.
  - Derivar `seq_tokens` do texto canônico com `split(' ')` (não reutilizar o parser de string concatenada de `scripts/algoritmo.py`).
  - Reutilizar `apply_filtro(musicas.values(), generos_key)` e `get_pagina(..., pagina_tag)` para preservar filtro de gênero, paginação e ordem atuais.
  - Montar cada item com os campos do branch atual: `id_unico_musica`, `id_artista`, `id_musica`, `nome_artista`, `nome_musica`, `popularidade`, `acordes`, `genero`, `url`. Não incluir `diferenca`/`intersecao`, senão `ng-hide="music.diferenca.length"` esconde os cards.
  - Manter `DB_PATH` em `data/db/` relativo à raiz do projeto (mesmo caminho do volume) e permitir override/banco temporário nos testes.
  - Performance: varredura do catálogo por request é aceitável no tamanho atual; sem cache nesta entrega.
  - Manter `json.dumps` e o cabeçalho CORS já aplicado por `after_request`.

### 5. [x] Alterar frontend em `#/porsequencia`
- [x] **5.1** Em `static/assets/js/controllers/sequencia.js`:
  - No init, `$http.get('sequencias')` e mapear `[{id, acordes}]` para `vm.sequenciasFamosas` no formato do template (`{id, acordes: [{acorde, cor: '#2E1C74'}]}`), dividindo a string por espaço.
  - Remover as 4 sequências hardcoded; tratar erro de carregamento com mensagem e lista vazia; seguir o padrão `.success/.error` do projeto.
  - Cadastro: manter a seleção ordenada em `vm.novaSequencia.acordes`; duplicar em `sequencia.js` os grupos de acordes hardcoded de `acordes.js` (decisão); clique acrescenta (não alterna), permitir repetição; remoção por índice; exibir prévia com `df-hex` e botão para limpar.
  - Submit: desabilitar quando vazio ou durante a requisição; enviar `POST sequencias` com `{"acordes": tokens.join(' ')}`; em `201`, limpar/fechar o picker e recarregar `GET /sequencias`; em `400`/`409`/erro de rede, mostrar mensagem específica (409: "sequência já existe") e manter o formulário.
  - Busca: trocar a concatenação manual por `$http.get('similares', {params: {sequencia: tokens.join(','), generos: vm.meuGenero}})` para codificar `#`, `&` e espaços; manter estados, `goToLirics`, `goToResults` e `limparPesquisa`.
  - A sequência cadastrada deve funcionar em `/similares?sequencia=...` como qualquer original.
- [x] **5.2** Em `static/templates/sequencia.html`:
  - Adicionar botão "Cadastrar nova sequência" abaixo da lista e painel expansível com picker, prévia ordenada e ações "Cadastrar"/"Cancelar".
  - Exibir estados: carregando lista, erro ao carregar, lista vazia, cadastro em andamento e mensagens de sucesso/erro (incluindo 409).
  - Renderizar a lista unificada com `ng-repeat="sequencia in Sequencia.sequenciasFamosas track by sequencia.id"` e manter o clique em `pesquisarPorSequencia`.
  - Manter busca, filtro de gênero e cards atuais; garantir que resultados sem `diferenca` continuem visíveis. Adicionar estado vazio "Nenhuma música encontrada" quando a busca não retornar itens.
  - Garantir layout responsivo do picker e da prévia na coluna esquerda.
  - Critério de aceite manual: cadastrar sequência (inclusive com `#`), recarregar a página, buscar por ela e ver os mesmos cards/links de cifra; tentar duplicata e ver a mensagem de conflito.

### 6. [x] Atualizar README e comando docker run com volume
- [x] **6.1** Atualizar `README.md` com instruções para persistência via volume.
- [x] **6.2** Documentar comando `docker run -p 8080:8080 -v ciframe-db:/app/data/db ciframe` (conforme `docs/adr/0002-persist-custom-sequences.md`).

### 7. [x] Teste de regressão das 6 sequências
- [x] **7.1** Testar busca para cada uma das 6 sequências originais e comparar a lista **ordenada** (não só o conjunto) com o baseline capturado antes do passo 4 (`tests/fixtures/similares_sequencias_baseline.json`), incluindo `pagina` quando aplicável e reproduzindo a ordem de gêneros registrada no baseline.
- [x] **7.2** Verificar que não há alteração nos resultados das originais; usar `artefatos/reppit/research/saida_validacao_matching.txt` como conferência adicional de conjunto.
- [x] **7.3** Atualizar `tests/test_regressao_sequencias.py` para comparar ordem/página, não apenas conjuntos.

## Arquivos afetados

| Arquivo | Mudança |
|---|---|
| `main.py` | Alterado (função de matching, inicialização do banco SQLite, população das 6 sequências originais, `GET /sequencias`, `POST /sequencias`, alteração em `GET /similares`) |
| `musica.py` | sem mudança |
| `static/assets/js/controllers/sequencia.js` | Alterado (carregar lista unificada, cadastro anônimo, busca unificada) |
| `static/templates/sequencia.html` | Alterado (interface de cadastro e lista unificada em `#/porsequencia`) |
| `static/assets/css/app.css` | Alterado (largura máxima do picker/prévia em telas estreitas) |
| `README.md` | Alterado (comando docker run com volume) |
| `.gitignore` | Alterado (adicionar data/db/) |
| `.dockerignore` | Alterado (adicionar data/db/) |
| Banco SQLite (novo arquivo em volume, ex. `data/db/`) | Novo (criado em runtime, populado na primeira execução com as 6 originais) |

## Riscos e mitigação

| Risco | Como perceber que deu errado | O que fazer |
|---|---|---|
| Banco não persistido (sem volume) | Após `docker rm` e `docker run` sem volume, sequências cadastradas somem. | Garantir montagem de volume conforme passo 6 e documentar no `README.md`. Usar caminho em `data/db/` preparado para volume. |
| Regressão nas 6 sequências originais | Busca pelas 6 sequências retorna resultados diferentes dos atuais. | Executar passo 7 comparando com `artefatos/reppit/research/saida_validacao_matching.txt` / comportamento atual. Ajustar função de matching para seguir exatamente a regra (1) sem acordes fora, (2) exata e sequencial ao menos uma vez, nessa ordem. |
| Matching incorreto (ordem/consecutivo ou acordes extras) | Músicas com acordes fora da sequência aparecem ou sequência não consecutiva/exata não é respeitada. | Seguir regra exatamente usando `musica.cifra` após `limpa_cifra` (conjunto para a regra 1 e ordem para a regra 2). Validar com `scripts/algoritmo.py`. |
| Arquivo do banco no caminho errado/sem permissão | Erro ao criar/gravar SQLite no startup. | Criar diretório `data/db/` com permissões adequadas, usar caminho consistente com volume montado. |
| Padronização incorreta na entrada do usuário | Cadastro aceita formato diferente e não encontra músicas. | Aplicar padronização: remover espaços sobrando e deixar primeira letra maiúscula por acorde (conforme `02-proposal.md`). |

## Definição de pronto

- [x] Cadastro de sequência funciona (anônimo) via `POST /sequencias`
- [x] Busca por sequência cadastrada funciona via `/similares` usando o matching em tempo real
- [x] As 6 sequências originais continuam funcionando como antes (teste de regressão - passo 7)
- [x] Banco SQLite criado em volume (ex. `data/db/`), tabela `sequencias` criada e populada com as 6 originais na primeira execução
- [x] `GET /sequencias` lista unificada (originais + customizadas)
- [x] `README.md` atualizado com comando `docker run` com volume
- [x] `.gitignore` e `.dockerignore` atualizados para `data/db/`
