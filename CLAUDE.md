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

### Como Rodar
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Endpoints Implementados
- `POST /transacoes` — cria transação, retorna 201 com objeto (inclui `id`)
- `GET /transacoes` — lista todas ordenadas por `data DESC`