# CLAUDE.md — Controle de Gastos Pessoais

## Decisões Técnicas Registradas

### Aula 1 - Transações
- **Banco de dados**: SQLite via `sqlite3` (biblioteca padrão Python) — sem dependências extras
- **ORM**: Não usado; SQL direto com `sqlite3.Row` para acesso por nome de coluna
- **Validação**: Pydantic v2 para schemas de request/response
- **Estrutura modular**:
  - `database/` — conexão e inicialização do schema
  - `models/` — Pydantic models (TransacaoCreate, TransacaoResponse)
  - `routes/` — endpoints FastAPI
  - `main.py` — entry point da aplicação

### Convenções de API
- Datas no formato ISO `YYYY-MM-DD` (serializadas via `date.isoformat()`)
- Valores monetários: `Decimal` com 2 casas decimais no modelo, `float` no SQLite
- `tipo` restrito a `"entrada"` ou `"saida"` (CHECK constraint no banco + Literal no Pydantic)
- Erros de validação: HTTP 422 com formato padrão do FastAPI/Pydantic (`detail` array com objetos de erro); **não** usa formato custom `{ "erro": "..." }`

### Decisões de Design — Categorias (Aula 3+)
- **Categoria em transação: OPCIONAL** (`categoria_id INTEGER NULL REFERENCES categorias(id)`). Usuário pode lançar sem categorizar; evita atrito no uso inicial.
- **Filtrar por categoria inexistente: retorna lista vazia (HTTP 200)**. Filtro é query param, não recurso; sem match → `[]` + 200. `GET /categorias/{id}` inexistente continua 404.

### Como Rodar
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Endpoints Implementados
- `POST /transacoes` — cria transação, retorna 201 com objeto (inclui `id`)
- `GET /transacoes` — lista todas ordenadas por `data DESC`