# deciframe

Descubra as músicas que você já sabe tocar (e ainda não faz ideia). Busque por
título/artista, gênero, pelos acordes que você já manja, ou por sequências de
acordes famosas — o deciframe cruza isso com uma base de cifras e sugere
músicas parecidas.

Stack: backend Flask (Python) servindo uma API JSON + um frontend AngularJS
estático. O catálogo de músicas é carregado do CSV em memória; as sequências
customizadas ficam em SQLite (`data/db/sequencias.db`).

## Rodando localmente

### Com Docker

```
docker build -t ciframe .
docker run -p 8080:8080 -v ciframe-db:/app/data/db ciframe
```

O volume nomeado `ciframe-db` mantém as sequências cadastradas entre execuções
e recriações do container. Sem o volume, o banco SQLite fica dentro do
container e é perdido quando ele é removido; as 6 sequências originais são
recriadas na próxima inicialização.

Acesse [http://localhost:8080](http://localhost:8080).

### Com virtualenv

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Acesse [http://localhost:5000](http://localhost:5000).

As sequências ficam em `data/db/sequencias.db`, criado automaticamente no
primeiro start. Para usar outro caminho, defina `CIFRAME_DB_PATH`.

### Testes

```
pip install -r requirements-dev.txt
python -m pytest tests -q
```

---

Para convenções de contribuição, veja [CONTRIB.md](CONTRIB.md). Licença: [LICENSE](LICENSE).
