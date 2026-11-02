## Solution Proposals

Context:
- Request: Adicionar nova feature — qualquer visitante poderá adicionar uma nova sequência famosa de acordes e fazer uma busca por músicas com ela. Essa sequência cadastrada deverá ser salva no banco de dados embarcado e deverá ser persistido de forma que se mantenha salvo em reinicios do docker.
- Research Source: `docs/features/sequencias-customizadas/01-research.md`, `research/bancos_embarcados_local_only.md`, `research/pagina_porsequencia.md`

### Proposal 1 — SQLite (stdlib) + persistência via volume montado
- Overview: Usar `sqlite3` (stdlib) para persistir sequências customizadas em arquivo único (ex.: `/app/data/custom_seqs.db` ou caminho montável). Tornar o matching em tempo real usando o critério validado: sequência aparece **exata e consecutivamente** em `musica.cifra` e **todos os acordes da música** estão apenas na sequência (`scripts/algoritmo.py`, `docs/features/sequencias-customizadas/01-research.md:72-92`). Manter arquitetura local-only e adicionar instrução de volume no Docker/README sem adicionar dependências novas.
- Key Changes:
  - `main.py:40-45` — estender mapa `sequencias` com entradas customizadas (carregadas do SQLite no startup). Alterar fluxo `/similares` (`main.py:225-273`) para suportar sequências customizadas (não apenas ids pré-computados) calculando matching em tempo real conforme critério validado.
  - `main.py` — novo endpoint para cadastro (ex.: `POST /sequencias-customizadas`) lendo payload, validando, persistindo no SQLite.
  - `data/` ou caminho configurável — criar schema `custom_sequences(id INTEGER PRIMARY KEY, sequence_key TEXT, tokens TEXT, created_at TIMESTAMP)`; arquivo `.db` gravável.
  - `Dockerfile` / `README.md` — documentar montagem de volume (ex.: `-v ${PWD}/data:/app/data`) para persistir arquivo `.db` entre recriações; hoje sem `VOLUME` (`research/bancos_embarcados_local_only.md:82-127`).
  - `static/templates/sequencia.html`, `static/assets/js/controllers/sequencia.js` — estender UI para cadastro (input/botões) e exibir sequências customizadas junto às hardcoded (`research/pagina_porsequencia.md:1-95`, `docs/features/sequencias-customizadas/01-research.md:127-144`).
- Trade-offs:
  - **Prós:** Sem nova dependência (`sqlite3` stdlib), simples, relacional, fácil de inspecionar. Alinha com "sem serviço externo adicional".
  - **Contras:** Precisa montar volume explicitamente (hoje não configurado) para sobreviver a `docker rm + run`. Concorrência escrita limitada (ok local). Exige mudanças em Docker/README.
- Validation:
  - Reproduzir validação com `scripts/algoritmo.py` para garantir critério exato-consecutivo + "sem acordes extras" (já validado 1.0).
  - Testar persistência: criar sequência customizada, `docker stop/start` mantém (camada gravável) e com volume mantem após `docker rm + run`.
  - Testar UI cadastro + busca `/similares` com sequência customizada.
- Open Questions:
  - Onde colocar arquivo `.db` (dentro de `data/` montável ou fora)? Precisa garantir escrita.
  - Esquema/versionamento? Normalização de tokens (hoje sem normalização).

### Proposal 2 — DuckDB (arquivo único) + persistência via volume montado
- Overview: Usar `duckdb` embarcado em arquivo único (`.duckdb`) para persistir sequências customizadas. Mesmo critério de matching em tempo real. Requer adicionar dependência e preparar binários no `python:3.9-slim`.
- Key Changes:
  - `requirements.txt` — adicionar `duckdb` (versão compatível com Python 3.9).
  - `main.py` — inicializar conexão DuckDB, criar tabela, carregar sequências customizadas no startup, endpoint POST, estender `/similares` com matching em tempo real.
  - `Dockerfile` — sem grande mudança estrutural, mas instalação de pacote nativo via pip (wheel geralmente disponível). Documentar volume.
  - `static/` — mesmas alterações de UI para cadastro/exibição.
- Trade-offs:
  - **Prós:** Ótimo para scans/consultas analíticas sobre CSV se integrado futuramente; API simples; arquivo único embarcado sem servidor.
  - **Contras:** Adiciona dependência ao `requirements.txt` (atualmente apenas Flask/gunicorn). Binário nativo no slim image. Precisa volume para persistir. Overhead maior se usado só como key-value simples.
- Validation:
  - Build da imagem com nova dependência. Testar matching igual ao validado. Testar persistência com volume.
- Open Questions:
  - Tamanho da imagem/compatibilidade wheel no `python:3.9-slim`. Necessidade real de OLAP vs relacional simples.

### Proposal 3 — TinyDB (JSON puro) + persistência via volume montado
- Overview: Usar `tinydb` (pure Python) gravando em arquivo JSON único (ex.: `data/custom_seqs.json`) para sequências customizadas. Matching em tempo real mesmo critério.
- Key Changes:
  - `requirements.txt` — adicionar `tinydb`.
  - `main.py` — ler/gravar JSON via TinyDB, endpoint POST, estender `/similares` com matching em tempo real.
  - `Dockerfile`/`README.md` — volume para arquivo JSON.
  - `static/` — UI para cadastro.
- Trade-offs:
  - **Prós:** Pure Python, sem extensões C, fácil no slim, simples para poucos registros.
  - **Contras:** Performance inferior para muitos registros/consultas complexas; concorrência limitada; menos "banco" tradicional. Precisa dependência. Precisa volume.
- Validation:
  - Testar CRUD simples, persistência, matching.
- Open Questions:
  - Escalabilidade irrelevante local? Atomicidade escrita em JSON.

## Comparação entre bancos (prós e contras diretos)
Baseado em `research/bancos_embarcados_local_only.md:1-127` e `docs/features/sequencias-customizadas/01-research.md:94-125`.

| Critério | SQLite (`sqlite3` stdlib) | DuckDB (`duckdb`) | TinyDB (`tinydb`) |
|---|---|---|---|
| Dependência em `requirements.txt` | Nenhuma (stdlib) | Sim, adicionar `duckdb` | Sim, adicionar `tinydb` |
| Tipo | Relacional embarcado, arquivo `.db` | OLAP embarcado, arquivo `.duckdb` | Document/JSON, arquivo `.json` |
| Persistência entre recriações Docker | Precisa volume montado (hoje não configurado). Sobrevive `stop/start` se não removido. | Precisa volume montado. | Precisa volume montado. |
| Mudanças em `Dockerfile` | Provavelmente nenhuma (só volume). | Nenhuma estrutural, instalação via pip ok se wheel. | Nenhuma estrutural. |
| Adequação ao caso (sequências + matching) | Muito bom - simples, relacional, suficiente | Bom mas overkill p/ lista simples; útil se analisar CSV depois | Bom p/ poucos itens, menos ideal p/ queries/concorrência |
| Facilidade no `python:3.9-slim` | Ótimo | Bom (wheel nativo) | Ótimo (pure Python) |
| Estado atual repo | Sem uso (`AGENTS.md:6-12`) | Sem uso | Sem uso |

## Notas obrigatórias (do research)
- Matching validado: exata e consecutiva + "sem acordes fora da sequência" reproduz matches das 6 hardcoded (`scripts/algoritmo.py`, `research/saida_validacao_matching.txt`). Não normalizar hoje (`docs/features/sequencias-customizadas/01-research.md:72-92`).
- Frontend atual tem 4 hardcoded diferentes das 6 do backend (`docs/features/sequencias-customizadas/01-research.md:127-144`, `research/pagina_porsequencia.md:49-52`).
- Hoje sem volume configurado → arquivo gravado dentro do container é perdido ao recriar (`research/bancos_embarcados_local_only.md:109-127`).
