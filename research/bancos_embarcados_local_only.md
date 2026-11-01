# Research: bancos embarcados viáveis dentro do container Docker único e local-only

Fonte orientadora consultada: https://deepwiki.com/joaoarthurbm/ciframe (usada como referência; confirmação feita diretamente no código-fonte).

## Resumo (3-6 sentenças)
O deploy atual é local-only via Docker único (`Dockerfile` usa `python:3.9-slim`, copia tudo, roda `gunicorn --bind 0.0.0.0:8080 main:app`; ADR 0001). O backend é `main.py` com dados carregados em memória a partir de `data/top/dataset_final.csv` no import, sem banco (`AGENTS.md`). `requirements.txt` tem apenas `Flask==3.1.3` e `gunicorn==23.0.0`. Considerando container único, local-only, sem serviço externo adicional e stack atual (Python 3.9, Flask), 3 opções viáveis de banco embarcado: **SQLite** (stdlib `sqlite3`, arquivo único no filesystem montado/volumes), **DuckDB** (arquivo único, bom para CSV/analytics, precisa adicionar dependência), **SQLite via APSW** não necessário; também **Berkeley DB** menos comum. As opções abaixo são viáveis dentro do mesmo container sem serviço externo.

## 3 opções viáveis

### 1) SQLite (biblioteca padrão)
- **Tipo:** Banco relacional embarcado, arquivo único (`.db`).
- **Como cabe no modelo atual:** Usa `import sqlite3` (stdlib) - sem dependência nova em `requirements.txt`. Pode ler CSV e popular DB em startup ou manter como está; arquivo pode ser persistido via volume montado localmente.
- **Vantagens (no contexto):** Zero dependência externa, nativo no Python, simples, funciona em container único local-only.
- **Limitações:** Menos otimizado para grandes scans analíticos que DuckDB; concorrência escrita limitada (ok para local).
- **Referências no repo:** Sem uso atual; arquitetura atual é in-memory (`main.py:66-113`).

### 2) DuckDB
- **Tipo:** OLAP embarcado, arquivo único (`.duckdb`) ou in-process.
- **Como cabe no modelo atual:** Pode consultar CSV diretamente (`read_csv_auto`) ou carregar em tabelas. Precisa adicionar `duckdb` a `requirements.txt` e instalar no container (pip). Arquivo persistido via volume.
- **Vantagens:** Ótimo para consultas sobre CSVs grandes, API Python simples, embarcado sem servidor.
- **Limitações:** Adiciona dependência, binário nativo no slim image (geralmente ok com pip wheel).
- **Referências no repo:** Sem uso atual.

### 3) LiteFS/sem servidor - ou **UnQLite**/**LevelDB**? Mais prático: **SQLite** já citado, **DuckDB**, **H2** não (JVM). Melhor terceira: **RocksDB** via `python-rocksdb` ou **plyvel** (LevelDB) - mas dependências C pesadas. Alternativa mais leve e viável: **SQLite com WAL**, ou **DuckDB**; terceira opção prática: **TinyDB** (JSON file, pure Python) - embarcado em arquivo único, sem C extensions pesadas, pode ir em requirements.
  - **TinyDB:** Arquivo JSON (`db.json`), pure Python, sem servidor. Viável em container slim. Menor performance para queries complexas, mas embarcado e sem deps nativas complicadas.
  - Ou **ZODB** (object DB) - menos comum para este caso tabular.

**Recomendadas concretas (viáveis no container único local-only):**
1. **SQLite** (`sqlite3` stdlib) - arquivo `.db`, sem nova dependência.
2. **DuckDB** (`duckdb` PyPI) - arquivo `.duckdb`, adiciona dependência mas embarcado sem serviço.
3. **TinyDB** (`tinydb` PyPI) - arquivo JSON, pure Python, sem extensões C, fácil no slim.

## Evidências do repo
- `Dockerfile`: único container, copia app inteiro, gunicorn porta 8080.
- `docs/adr/0001-local-only-docker-deploy.md`: local-only, sem plataforma cloud definida.
- `AGENTS.md`: "Single file (`main.py`) that loads `data/top/dataset_final.csv` into memory once at startup — there is no database."
- `requirements.txt`: apenas Flask, gunicorn.

## Conexões
Mudança para qualquer um desses exigiria persistir arquivo via volume (Docker) para manter dados entre execuções se necessário, mas todos são embarcados no mesmo container sem serviço externo adicional.

## Complemento: como o container é iniciado hoje e persistência

### Como é iniciado (conforme repo)
- `Dockerfile` (`Dockerfile:1-12`):
  - `FROM python:3.9-slim`
  - `WORKDIR /app`
  - `COPY requirements.txt .`
  - `RUN pip install --no-cache-dir -r requirements.txt`
  - `COPY . .`
  - `EXPOSE 8080`
  - `CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]`
- Comando documentado: `docker build -t ciframe .` e `docker run -p 8080:8080 ciframe` (`README.md:19-24`, `AGENTS.md:39-48`).
- `AGENTS.md:58-59`: "Editing `data/top/*.csv` requires a restart: it's read once at import time, not per-request." (carga em memória em import de `main.py`).
- Porta exposta 8080, bind em `0.0.0.0:8080`.

### O que existe no filesystem do container hoje
Copiado com `COPY . .` para `/app` (`Dockerfile:9`). Arquivos presentes no repo (vistos): `main.py`, `musica.py`, `requirements.txt`, `data/` (com `data/top/dataset_final.csv`), `static/`, `docs/`, `research/`, `scripts/`, etc. Tudo copiado na imagem é imutável na camada da imagem.

### Persistência entre reinícios/recriação
- **Ao reiniciar o container** (`docker start <container>`): o filesystem de camadas graváveis (container layer) permanece se o container não foi removido. Arquivos escritos em tempo de execução no container (não em volume montado) sobrevivem ao `stop/start`. Porém, como não há volumes definidos no `Dockerfile`, nem instruções de volume, o padrão é sem persistência externa.
- **Ao recriar o container** (`docker rm` + `docker run`, ou `docker compose down` sem volumes): **descartado**. Todo filesystem gravável do container anterior é removido; um novo container é criado a partir da imagem, com `COPY . .` da imagem (estado original da imagem). Arquivos modificados/criados no container antigo **não sobrevivem** à recriação.
- **Volumes**: não há `VOLUME` no `Dockerfile` e nenhuma menção a volumes nos docs/ADR/README/AGENTS analisados. Portanto, hoje **não há diretórios garantidamente persistentes** configurados; qualquer escrita fora da imagem só persiste enquanto o container existe. Para persistir dados entre recriações seria necessário montar um volume (não configurado atualmente).

**Conclusão prática:** diretórios graváveis do container existem enquanto o container não for removido (`stop/start` pode manter escrita em camada gravável), mas **ao recriar o container (rm + run) tudo é descartado** exceto o que estiver em volumes montados explicitamente - e **não há volumes configurados hoje**. Dados lidos de `data/top/dataset_final.csv` vêm da imagem (copiados) e são carregados em memória no import de `main.py`.
