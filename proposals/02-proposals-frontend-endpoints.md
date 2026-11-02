## Solution Proposals

Context:
- Request: Adicionar feature — qualquer visitante poderá adicionar uma nova sequência famosa de acordes e fazer busca por músicas com ela. Sequência cadastrada deve ser salva no banco de dados embarcado **SQLite** e persistida para sobreviver a reinícios do docker. Requisitos obrigatórios: sem login; qualquer sequência (6 originais + novas) pode ser usada para buscar.
- Research Source: `docs/features/sequencias-customizadas/01-research.md`, `research/pagina_porsequencia.md`, `research/bancos_embarcados_local_only.md`, `scripts/algoritmo.py`, `research/saida_validacao_matching.txt`

### Proposal 1 — Campo de texto + endpoint REST para cadastro/listagem (unificado com `/similares`)
- Overview: Adicionar um campo de texto na `#/porsequencia` para o visitante digitar a sequência (ex.: `Bm,G,D,A` ou tokens concatenados como hoje). Backend persiste no SQLite em `data/custom/sequencias_customizadas.db` (criado em runtime), carrega customizadas no startup e as une ao `sequencias` (mapa hardcoded). Cadastro via `POST /sequencias-customizadas` sem autenticação. Busca continua pelo mesmo fluxo `/similares?sequencia=...` mas backend passa a aceitar sequências customizadas (busca em tempo real pelo critério validado: **exata e consecutiva** + **todos os acordes da cifra apenas na sequência**). Persistência garantida via volume montado em `./data:/app/data` (hoje sem volume configurado).

- Key Changes:
  - **Banco SQLite:** criar `data/custom/` (`os.makedirs`), tabela `custom_sequences(id INTEGER PRIMARY KEY, sequence_key TEXT UNIQUE, tokens_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`. Arquivo: `data/custom/sequencias_customizadas.db`.
  - **Backend `main.py`:**
    - Carregar customizadas no startup (após ler CSV) e popular `sequencias_customizadas = {}` unindo ao mapa usado por `/similares` (`main.py:40-45,194-197`).
    - **Novo endpoint:** `POST /sequencias-customizadas` — sem login. Body JSON: `{"sequencia":"Bm,G,D,A"}` ou `{"tokens":["Bm","G","D","A"]}`. Normalizar para string-chave sem vírgulas (igual ao formato esperado pelo fluxo atual). Validar não-vazio. Salvar com `INSERT OR IGNORE`. Retornar 201/200 com `{id, key, tokens}`.
    - **Novo endpoint:** `GET /sequencias-customizadas` — lista todas (originais + customizadas) para popular UI: retorna array com `{key, source:'original'|'custom', tokens:[...]}` (facilita exibir no frontend).
    - **Alterar `/similares` (`main.py:189-197`):** se `sequencia_tag` não está em `sequencias` hardcoded, procurar em `sequencias_customizadas`. Para qualquer sequência (hardcoded ou customizada) que não tenha match via tag pré-computada, **calcular em tempo real** usando `musica_contem_sequencia` lógica equivalente a `scripts/algoritmo.py:144-156` (exata e consecutiva + sem acordes extras). Manter filtro de gênero via `apply_filtro` (`main.py:249-273`).
    - **Persistência:** garantir escrita no arquivo em `data/custom/` e documentar montagem de volume no `README.md`/operacional (sem alterar arquitetura para serviço externo).
  - **Frontend `static/templates/sequencia.html` (`#/porsequencia`):**
    - Adicionar seção "Cadastrar nova sequência" com input texto (placeholder `Ex: Bm,G,D,A`) e botão "Cadastrar e buscar".
    - Exibir lista unificada: carregar via `GET /sequencias-customizadas` e renderizar com `ng-repeat` (substituir/aproximar hardcoded `Sequencia.sequenciasFamosas` por dados do backend).
    - Manter exibição dos acordes clicáveis e filtro de gênero.
  - **Frontend `static/assets/js/controllers/sequencia.js`:**
    - Carregar sequências via `$http.get('sequencias-customizadas')` no init.
    - `vm.cadastrarSequencia(input)` — `$http.post('sequencias-customizadas', {...})` sem auth; em sucesso recarregar lista e chamar `vm.pesquisarPorSequencia(...)` com a nova sequência.
    - `createChordsString` continua compatível (separa por vírgula). Ao buscar, funciona para qualquer sequência retornada pelo backend.
    - Manter `vm.pesquisarPorSequencia`, `vm.goToLirics`, filtro por gênero.

- Trade-offs:
  - **Prós:** Rápido para usuário (digitação), mínimo de mudanças visuais, reutiliza fluxo `/similares` existente, fácil de validar com `scripts/algoritmo.py`. Sem dependências novas.
  - **Contras:** Digitação livre exige validação no backend/frontend (strings inválidas). Não aproveita botões tipo página `/poracordes`. Possível entrada com espaços/variações.

- Validation:
  - Criar sequência customizada → aparece em `GET /sequencias-customizadas` → persiste em SQLite. Reiniciar container com volume montado (`-v ./data:/app/data`) → continua existente. Sem volume, persiste apenas enquanto container não for removido (documentar).
  - Buscar com customizada retorna músicas pelo critério exato-consecutivo + sem acordes extras. Buscar com 6 originais mantém comportamento.
  - Validar contra `scripts/algoritmo.py` lógica.

- Open Questions:
  - Formato aceito (vírgulas vs espaços)? Normalizar tokens.
  - Duplicados (case/whitespace)?
  - Limitar tamanho/tokens?

### Proposal 2 — Seletor de botões (tipo `/poracordes`) + mesmo backend persistente
- Overview: Na `#/porsequencia`, adicionar construtor por botões (seleção de acordes em ordem) similar à experiência de `/poracordes`, permitindo montar a sequência clicando botões. Mesmo backend SQLite em `data/custom/sequencias_customizadas.db`, mesmos endpoints `POST /sequencias-customizadas` e `GET /sequencias-customizadas`, mesmo matching em tempo real e mesmo requisito de persistência via volume.

- Key Changes:
  - **Backend:** Idênticos ao Proposal 1 (SQLite em `data/custom/`, endpoints sem login, unificação de listas, matching em tempo real pelo critério validado). A diferença é apenas no formato de entrada aceito (botões geram array de tokens já no formato correto).
  - **Frontend `static/templates/sequencia.html`:**
    - Substituir/adicionar painel "Montar sequência" com grade de botões de acordes (inspirado em `/poracordes`). Exibir sequência montada em ordem com botões/remover.
    - Botão "Cadastrar nova sequência" e "Buscar com esta sequência" (pode cadastrar e buscar simultaneamente).
    - Exibir lista unificada de sequências (originais + customizadas) clicáveis igual hoje.
  - **Frontend `static/assets/js/controllers/sequencia.js`:**
    - Manter lista de acordes disponíveis (pode ser subset; trade-off mencionado em pesquisa). Montar `vm.novaSequencia = {acordes: [...]}` igual estrutura usada por `vm.minhaSequencia`.
    - `vm.adicionarAcorde(acorde)` / `vm.removerAcorde(index)` / `vm.limparNovaSequencia()`.
    - `vm.cadastrarENotarBuscar()` — `POST` com tokens gerados pelos botões; após cadastro recarregar lista e chamar `vm.pesquisarPorSequencia` com objeto no mesmo formato usado hoje (`acordes:[{acorde,cor},...]`).
    - Carregar customizadas via `GET /sequencias-customizadas`.

- Trade-offs:
  - **Prós:** Reduz erros de digitação, entrada no formato esperado pelo backend, melhor UX para leigos.
  - **Contras:** `docs/features/sequencias-customizadas/01-research.md:127-144` aponta poluição visual na página que já mostra sequências cadastradas, limite de acordes nos botões (CSV tem `maj7`, `add9`, inversões `/`, variações) — ou precisa lista extensa/pesquisa de acordes, maior complexidade no frontend AngularJS 1.4.9.

- Validation:
  - Montar sequência por botões → cadastrar → persistir no SQLite → buscar pelo critério validado. Testar persistência com volume.

- Open Questions:
  - Quais acordes disponibilizar nos botões? Cobrir todas as variações do CSV ou permitir livre? Se limitar, restringe sequências cadastráveis.

## Formato de entrada/saída (detalhado)
- **Banco:** SQLite em `data/custom/sequencias_customizadas.db`, tabela `custom_sequences`.
  - `sequence_key TEXT UNIQUE` — string concatenada sem vírgulas (igual formato usado pelo fluxo `/similares`: `acordes = sequencia_tag.replace(',','')` em `main.py:191,194`).
  - `tokens_json TEXT` — JSON array com tokens individuais.
- **POST `/sequencias-customizadas` (sem login):**
  - Request (Proposal 1): `{"sequencia": "Bm,G,D,A"}` OR `{"tokens": ["
