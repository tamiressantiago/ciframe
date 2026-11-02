# Proposta — Sequências de Acordes Customizadas

## Abordagem escolhida

### Algoritmo de matching

Para que uma música seja compatível com uma sequência, deverá ser verificado:

1. A música não poderá ter acordes fora da sequência indicada
2. Na música, os acordes da sequência deverão aparecer na ordem exata e de forma sequêncial ao menos 1 vez

É interessante que a verificação seja feita nesta ordem, pois como temos `musica.acordes` (acordes únicos) será rápido verificar e descartar as músicas que já não cumpram com a condição 1.

Essa regra é adequada porque ela reproduz exatamente as músicas com tag `SEQ_FAMOSA` nas 6 sequências existentes (`research/saida_validacao_matching.txt`). A tag SEQ_FAMOSA do CSV deixa de ser usada na busca, já que o matching passa a ser calculado em tempo real para todas as sequências.

### Banco de dados

Usei a ferramenta /make-proposals para criar propostas sobre os bancos pesquisados em 01-research.md (proposals/solution_proposals_sequencias_customizadas.md). O SQLite foi escolhido por já vir na imagem, sem precisar adicionar uma dependência nova em `requirements.txt`. Só o catálogo de sequências vai para o banco. As músicas e os gêneros continuam vindo do CSV, carregados em memória como hoje. Na busca, a sequência é lida do banco e comparada com as músicas carregadas do CSV, então o banco apenas guarda e devolve para o front a lista de acordes de cada sequência.

Para a persistência, o banco será um arquivo local e precisa ficar em volume. Sem isso, as sequências vão se perder quando o container for recriado. O arquivo ficará em `data/db/`. Na primeira execução, o banco será criado com as 6 sequências originais.

Para manter o volume, o comando de execução deverá passar a ser: `docker run -p 8080:8080 -v ciframe-db:/app/data/db ciframe`.

### Esquema de dados (alto nível)

O banco terá a tabela `sequencias`, que guarda todas as sequências do catálogo (as 6 originais e as cadastradas pelos usuários). Cada linha terá um `id` (inteiro, chave primária) e os `acordes`. Os acordes serão guardados como um texto com os acordes separados por espaço (por exemplo, `Bm G D A`).

### API

Novos endpoints:
- `GET /sequencias` — Lista todas as sequências do catálogo (as 6 originais e as cadastradas). Retorna a lista com o id e os acordes de cada sequência.
- `POST /sequencias` — Cadastra uma nova sequência. Recebe um corpo como `{"acordes": "Bm G D A"}`. Retorna `201 Created` se a sequência for criada, se a sequência vier vazia retorna `400 Bad Request`.

Endpoint alterado:
- `GET /similares` — Passa a buscar a sequência no banco, e não mais nas 6 sequências fixas do `main.py`, então funciona para as originais e para as cadastradas. Recebe a sequência como hoje (`GET /similares?sequencia=C,G,Am,F`) e mantém o filtro opcional de gêneros.

### Frontend

Na página #/porsequencia, a lista de sequências deixa de ser fixa no JavaScript e passa a ser carregada do backend, pelo `GET /sequencias`, mostrando as 6 originais e as cadastradas. Abaixo dessa lista, teremos um novo botão chamado "Cadastrar nova sequência". Ao clicar neste botão, será exibida uma lista dos acordes disponíveis, da mesma forma que já acontece em #/poracordes. Assim, o usuário seleciona os acordes e cadastra a nova sequência no sistema.

## Alternativas consideradas e descartadas

Foi considerada a alternativa do frontend exibir uma caixa de texto onde o usuário digitaria os acordes da sequência desejada. Ela foi descartada porque aceita erros de digitação, o que permitiria cadastrar acordes que não existem e exigiria mais validação da entrada no frontend. A escolha dos acordes por botões reduz esse problema.

## Escopo explícito

**Dentro do escopo:**
- Cadastro de novas sequências por qualquer visitante, sem login, pelo endpoint `POST /sequencias`.
- Listagem do catálogo (as 6 originais e as cadastradas) pelo endpoint `GET /sequencias`.
- Persistência do catálogo em SQLite, em volume, para sobreviver à recriação do container.
- Busca de músicas por qualquer sequência do catálogo, com matching calculado em tempo real, pela regra validada nas 6 sequências originais.
- Alteração do `GET /similares` para buscar a sequência no banco.
- Página `#/porsequencia` lendo o catálogo do backend e permitindo cadastrar uma nova sequência.

**Fora do escopo (e por quê):**
- Login/autenticação.
- Alterações no carregamento do CSV ou estrutura de `Musica`.
- Editar ou remover sequências cadastradas.
