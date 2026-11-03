# Plano — Sequências de Acordes Customizadas

## Passos

### 1. [ ] Definir função de matching
- [ ] **1.1** Analisar a regra em `docs/features/sequencias-customizadas/02-proposal.md`: (1) a música não pode ter acordes fora da sequência indicada; (2) a sequência deve aparecer na ordem exata e de forma sequencial ao menos uma vez (verificar nessa ordem).
- [ ] **1.2** Criar função seguindo padrão existente no `main.py`. Sugestão de nome: `musica_tem_sequencia(musica, seq_tokens)` ou reutilizar lógica similar a `scripts/algoritmo.py:musica_contem_sequencia(cifra, seq_tokens)`. A função deve:
  - Usar `musica.acordes` (conjunto/lista de acordes únicos) para verificar (1) — "sem acordes fora da sequência"
  - Usar `musica.cifra` (lista na ordem) após `limpa_cifra` (`main.py:15-29`) para verificar (2) — aparece na ordem exata e de forma sequencial ao menos uma vez
- [ ] **1.3** Verificar with `scripts/algoritmo.py` and `research/saida_validacao_matching.txt` that the logic reproduces matches of the 6 originals. Não fazer normalização ampla das cifras.

### 2. [ ] Criar banco SQLite e popular com as 6 sequências originais
- [ ] **2.1** Usar `sqlite3` da stdlib. Definir caminho para arquivo do banco em pasta própria para volume, ex.: `data/db/` (criar diretório se não existir).
- [ ] **2.2** Criar tabela `sequencias`:
  - `id` INTEGER PRIMARY KEY
  - `acordes` TEXT (acordes separados por espaço, ex.: `Bm G D A`)
- [ ] **2.3** Na primeira execução (startup), popular com as 6 sequências originais de `main.py:40-45` (inserir apenas se não existirem).
- [ ] **2.4** Garantir que o arquivo seja gravado no caminho preparado para volume.

### 3. [ ] Atualizar .gitignore e .dockerignore para data/db/
- [ ] **3.1** Adicionar `data/db/` em `.gitignore`.
- [ ] **3.2** Adicionar `data/db/` em `.dockerignore`.

### 4. [ ] Adicionar endpoints mencionados no 02-proposal.md
- [ ] **4.1** **GET /sequencias-customizadas** — lista unificada (6 originais + customizadas). Retornar estrutura compatível com uso no frontend.
- [ ] **4.2** **POST /sequencias-customizadas** — cadastro anônimo (sem login). Aceitar entrada e padronizar: remover espaços sobrando e deixar primeira letra maiúscula por acorde. Salvar no banco SQLite.
- [ ] **4.3** **Alterar GET /similares (`main.py:189-197`)** — aceitar sequências originais ou customizadas. Para customizadas (ou quando não resolvido apenas por tag pré-computada), aplicar a função de matching em tempo real. Manter filtro `generos` opcional.

### 5. [ ] Alterar frontend em `#/porsequencia`
- [ ] **5.1** Em `static/assets/js/controllers/sequencia.js`: carregar lista unificada via `GET /sequencias-customizadas` no init; adicionar lógica de cadastro anônimo chamando `POST /sequencias-customizadas`; manter fluxo de busca via `/similares?sequencia=...` para qualquer sequência (antiga ou nova).
- [ ] **5.2** Em `static/templates/sequencia.html`: adicionar interface para cadastro de nova sequência e exibir lista unificada (originais + customizadas), permitindo busca pelo mesmo jeito de hoje.

### 6. [ ] Atualizar README e comando docker run com volume
- [ ] **6.1** Atualizar `README.md` com instruções para persistência via volume.
- [ ] **6.2** Documentar comando `docker run -p 8080:8080 -v ciframe-db:/app/data/db ciframe` (conforme `docs/adr/0002-persist-custom-sequences.md`).

### 7. [ ] Teste de regressão das 6 sequências
- [ ] **7.1** Testar busca para cada uma das 6 sequências originais.
- [ ] **7.2** Comparar com comportamento atual / `research/saida_validacao_matching.txt`.
- [ ] **7.3** Verificar que não há alteração nos resultados das originais.

## Arquivos afetados

| Arquivo | Mudança |
|---|---|
| `main.py` | Alterado (função de matching, inicialização do banco SQLite, população das 6 sequências originais, `GET /sequencias-customizadas`, `POST /sequencias-customizadas`, alteração em `GET /similares`) |
| `musica.py` | sem mudança |
| `static/assets/js/controllers/sequencia.js` | Alterado (carregar lista unificada, cadastro anônimo, busca unificada) |
| `static/templates/sequencia.html` | Alterado (interface de cadastro e lista unificada em `#/porsequencia`) |
| `README.md` | Alterado (comando docker run com volume) |
| `.gitignore` | Alterado (adicionar data/db/) |
| `.dockerignore` | Alterado (adicionar data/db/) |
| Banco SQLite (novo arquivo em volume, ex. `data/db/`) | Novo (criado em runtime, populado na primeira execução com as 6 originais) |

## Riscos e mitigação

| Risco | Como perceber que deu errado | O que fazer |
|---|---|---|
| Banco não persistido (sem volume) | Após `docker rm` e `docker run` sem volume, sequências cadastradas somem. | Garantir montagem de volume conforme passo 6 e documentar no `README.md`. Usar caminho em `data/db/` preparado para volume. |
| Regressão nas 6 sequências originais | Busca pelas 6 sequências retorna resultados diferentes dos atuais. | Executar passo 7 comparando com `research/saida_validacao_matching.txt` / comportamento atual. Ajustar função de matching para seguir exatamente a regra (1) sem acordes fora, (2) exata e sequencial ao menos uma vez, nessa ordem. |
| Matching incorreto (ordem/consecutivo ou acordes extras) | Músicas com acordes fora da sequência aparecem ou sequência não consecutiva/exata não é respeitada. | Seguir regra exatamente usando `musica.acordes` (ponto 1) e `musica.cifra` após `limpa_cifra` (`main.py:15-29`) (ponto 2). Validar com `scripts/algoritmo.py`. |
| Arquivo do banco no caminho errado/sem permissão | Erro ao criar/gravar SQLite no startup. | Criar diretório `data/db/` com permissões adequadas, usar caminho consistente com volume montado. |
| Padronização incorreta na entrada do usuário | Cadastro aceita formato diferente e não encontra músicas. | Aplicar padronização: remover espaços sobrando e deixar primeira letra maiúscula por acorde (conforme `02-proposal.md`). |

## Definição de pronto

- [ ] Cadastro de sequência funciona (anônimo) via `POST /sequencias-customizadas`
- [ ] Busca por sequência cadastrada funciona via `/similares` usando o matching em tempo real
- [ ] As 6 sequências originais continuam funcionando como antes (teste de regressão - passo 7)
- [ ] Banco SQLite criado em volume (ex. `data/db/`), tabela `sequencias` criada e populada com as 6 originais na primeira execução
- [ ] `GET /sequencias-customizadas` lista unificada (originais + customizadas)
- [ ] `README.md` atualizado com comando `docker run` com volume
- [ ] `.gitignore` e `.dockerignore` atualizados para `data/db/`
