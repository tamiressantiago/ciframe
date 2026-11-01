# Pesquisa — Sequências de Acordes Customizadas

## Perguntas que você precisa responder

1. **Algoritmo de matching**: hoje, as 6 sequências hardcoded em `main.py` (linhas
   40-45) são comparadas contra músicas via uma tag pré-computada
   (`SEQ_FAMOSA`/`seqs_famosas`, vinda do CSV). Sequências cadastradas pelo usuário
   não têm essa tag — o matching precisa ser calculado em tempo real a partir da
   lista de acordes de cada música (`musica.acordes`/`musica.cifra`). O que vai
   definir "a sequência X aparece na música Y"? A ordem dos acordes importa?
   Repetições de acorde dentro da música importam? É preciso normalizar (ex.:
   maiúsculas/minúsculas, variações de escrita do mesmo acorde)?
2. **Validação da hipótese**: rode o algoritmo que você está considerando contra os
   dados reais em `data/top/dataset_final.csv`, para as 6 sequências hoje
   hardcoded, e confirme (ou refute) que ele reproduz os mesmos matches que o
   código atual produz via `seqs_famosas`. Esse é o bar mínimo de correção que
   você vai usar na fase de testes.
3. **Banco de dados**: quais bancos embarcados (sem serviço externo adicional) são
   viáveis dentro do container Docker único e local-only já documentado em
   `docs/adr/0001-local-only-docker-deploy.md`? O que cada opção implica para o
   `Dockerfile` atual e para a persistência dos dados entre reinícios do
   container?
4. **Frontend existente**: o que a página `#/porsequencia`
   (`static/templates/sequencia.html` +
   `static/assets/js/controllers/sequencia.js`) já faz? Repare que ela tem hoje uma
   lista *hardcoded no JavaScript* de 4 sequências (`sequencia1`..`sequencia4`),
   diferente das 6 que existem no backend — um detalhe real e pré-existente do
   código, não um erro seu, que vale entender antes de decidir o que precisa
   mudar.

## Registro das descobertas

   1. Algoritmo de matching: Na busca, uma música tem a sequência famosa quando a sequência aparece de forma exata e consecutiva em algum ponto da cifra e a música não usa nenhum acorde fora da sequência. Comecei achando que existia apenas a primeira condição, porque toda música marcada com uma sequência famosa a contém de forma exata e consecutiva (docs/research/exemplo_sequencia_nunca_exata.md e docs/research/analise_padrao_cifra_sequencial_famosa.md). Mas, ao executar o algoritmo contra os dados, vi que só essa condição não reproduzia os matches do código original. Ao acrescentar a segunda, o resultado passou a bater com a tag nas 6 sequências. Confirmei a necessidade dessa condição ao usar a ferramenta /research-codebase para procurar no dataset_final.csv por alguma cifra com tag de sequência famosa que tivese acordes fora dessa sequência, tendo como resultado 0 ocorrências (docs/research/acordes_fora_da_sequencia_famosa.md).

   A posição da sequência não importa, pois ela pode aparecer no início, no meio ou no fim da música. A repetição da sequência ao longo da música também não importa, basta que ela apareça ao menos uma vez. Já a repetição de um mesmo acorde em posições seguidas quebra a ordem exata esperada, mesmo que seja um acorde da própria sequência (por exemplo, para a sequência BmGDA, BmGGDA não funciona). Por fim, atualmente a normalização existente das cifras limpa apenas tablaturas (docs/research/normalizacao_cifras.md, docs/research/padrao_maiusculas_cifras.md e conferido na função limpa_cifra() no main 11-23). As cifras também não seguem a mesma notação (docs/research/padrao_musical_cifras.md).

   2. Validação da hipótese: Informei as caracteristicas que eu queria no algoritmo para o opencode e solicitei a criação dele (presente em scripts/algoritmo.py). O algoritmo reproduz os mesmos matches que o código atual produz (saída com comparações em docs/research/saida_validacao_matching.txt).

   3. Banco de dados: Executei o comando /research-codebase e pedi 3 opções de bancos embarcados viáveis nesse contexto (docs/research/bancos_embarcados_local_only.md), e o resultado foi SQLite, DuckDB e TinyDB. O SQLite já vem no Python, então não exige dependência nova. O DuckDB e o TinyDB não vêm e precisariam ser acrescentados ao requirements.txt. As três opções gravam em um arquivo local. Hoje o Dockerfile não declara volume (Dockerfile) e o comando docker run -p 8080:8080 ciframe (README.md:19-24) também não monta nenhum, então um arquivo gravado dentro do container é perdido quando o container é recriado.

   4. Frontend existente: A página #/porsequencia busca músicas através de uma sequência famosa de acordes. Em static/assets/js/controllers/sequencia.js, exibe 4 sequências famosas de forma hardcoded (linhas 2-31) e realiza o GET através da função pesquisarPorSequencia(), que também apresenta um filtro opcional de gênero (linhas 63-90). A página também permite que, quando o usuário clique no cartão da música, ele seja direcionado para a página da crifra (static/templates/sequencia.html na linha 45 e static/assets/js/controllers/sequencia.js em 97-99).

## Trade-offs identificados

Para o algoritmo, não normalizar é a opção mais simples e foi suficiente para reproduzir os mesmos matches do código atual, mas faz uma sequência só casar com músicas que a escrevam exatamente igual. Normalizar aumentaria os resultados, mas teria que ser aplicado tanto à sequência do usuário quanto às cifras, exigiria decidir quais variações unificar e poderia alterar os matches que o código atual faz.

Para o banco de dados, o SQLite não exige dependência nova, pois já vem no Python, o DuckDB e o TinyDB exigem acrescentar um pacote ao requirements.txt. As três opções gravam em arquivo local, então o arquivo é perdido quando o container é recriado, e qualquer opção exigiria alterar o Dockerfile e/ou o comando de execução do README para persistir os dados.

No frontend, poderíamos ter a opção do usuário cadastrar a sequência através de um botão para cada acorde, de forma similar ao que é feito na página #/poracordes. A vantagem é que a entrada virá já no formato esperado, reduzindo erros de digitação. A desvantagem é a poluição visual que esses botões adicionariam na página, pois diferente da #/poracordes, a #/porsequencia também mostra as sequências já cadastradas. Além disso, o CSV usa diferentes tipos de acordes (maj7, add9, inversões com /), então um conjunto fixo de botões limitaria as sequências possíveis ou seria necessário muitos botões. Poderíamos também ter apenas um campo de texto para o usuário digitar, mas essa opção precisa de validação e aceita erros de digitação.
