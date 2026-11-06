# Relatório de testes — Sequências de Acordes Customizadas

## Cobertura

A suíte automatizada tem 80 testes e cobre apenas a funcionalidade nova do plano:

- `tests/test_matching.py`: `normalizar_sequencia`, `has_exact_consecutive_sequence`, `musica_contem_sequencia` e `musica_tem_sequencia` (matching em tempo real sobre `musica.cifra`, sem depender de `seqs_famosas`).
- `tests/test_sequencias_api.py`: `GET /sequencias`, `POST /sequencias` (201, 400, 409, 413 e 500), normalização de entrada, duplicatas, acordes com `#`, limites de 20 acordes/30 caracteres/2 KB, CORS e Content-Type legado.
- `tests/test_similares.py`: busca pelas 6 originais, sequência customizada após cadastro, sequência com `#`, filtro por gênero, sequência inexistente/vazia, paginação, formato dos itens e erro de banco.
- `tests/test_db.py`: criação do diretório/arquivo, seed idempotente das 6 originais, constraint `UNIQUE`, persistência após reabertura e dois POSTs concorrentes da mesma sequência (201 + 409).
- `tests/test_regressao_sequencias.py`: comparação dos conjuntos com as tags `seqs_famosas` e comparação ordenada, página a página, com o baseline capturado antes da migração.

Em todos os testes que tocam banco, `tests/conftest.py` usa um SQLite temporário por teste via `CIFRAME_DB_PATH`, sem alterar `data/db/sequencias.db`.

## Teste de regressão obrigatório

As 6 sequências originais estão em `main.py:16-23` (`SEQUENCIAS_ORIGINAIS`).

O baseline foi capturado antes de desligar o caminho por tag e está versionado em `tests/fixtures/similares_sequencias_baseline.json`. Para cada uma das 6 sequências, a suíte:

1. compara o conjunto de músicas encontradas por `musica_contem_sequencia` com o conjunto de músicas que possuem a tag `seqs_famosas` correspondente;
2. chama `GET /similares` página a página, usando a mesma ordem de gêneros registrada no baseline, e compara a lista ordenada de `id_unico_musica` com a lista esperada;
3. confere que o total encontrado coincide com o total do baseline.

Resultado: as 6 sequências mantêm os mesmos conjuntos, a mesma ordem e a mesma paginação. A suíte completa termina com **80 passed**.

## Como rodar

```
pip install -r requirements-dev.txt
python -m pytest tests -q
```

## O que ficou de fora

- Contratos legados (`/search`, `/musicas`, `/generos`, `/acordes`, `/musica/<id>` e helpers não alterados): não foram retestados porque não fazem parte da funcionalidade nova; a regressão cobre o impacto da migração nas 6 sequências.
- Testes automatizados de interface: o frontend AngularJS não tem suíte de browser. O cadastro, recarregamento da lista, busca por sequência cadastrada (inclusive com `#`) e mensagem de duplicata foram validados apenas no backend e precisam de conferência manual em `#/porsequencia`.
- Migração de bancos SQLite criados por versões intermediárias desta feature: os testes cobrem criação/seed de banco novo, não uma migração de schema.
- Teste de integração com Docker/volume: a persistência é validada diretamente no SQLite; a montagem real do volume não é exercitada pela suíte.
- Testes de carga/performance: a busca por sequência percorre o catálogo em memória a cada request. Isso é aceitável para o tamanho atual, mas não há teste de volume ou benchmark.
- Limites de abuso além do tamanho do corpo/quantidade de acordes: não há rate limiting nem autenticação, por decisão do escopo (endpoint anônimo e deploy local-only).
- Startup concorrente de múltiplos workers do gunicorn: há teste de POSTs concorrentes, mas não de múltiplos processos executando o seed simultaneamente.
