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

### Aula 2 - CRUD Completo e Validação
- **PUT /transacoes/{id}** — atualiza transação (todos os campos editáveis); retorna 200 com objeto atualizado ou 404
- **DELETE /transacoes/{id}** — exclui transação; retorna 204 ou 404
- **Validação centralizada nos schemas Pydantic**:
  - `valor` > 0 (Decimal com 2 casas decimais)
  - `tipo` restrito a `"entrada"` ou `"saida"` (Literal)
  - `data` formato ISO válido (date)
  - `descricao` não vazia (min_length=1, max_length=200)
- **Erros de validação**: HTTP 422 com formato padrão FastAPI/Pydantic (`detail` array); **não** usa formato custom `{ "erro": "..." }`

### Aula 3 - Categorias e Filtro
- **Models**: CategoriaCreate, CategoriaResponse (nome único, max 100 chars)
- **Endpoints**:
  - `POST /categorias` — cria categoria; nome duplicado retorna 422
  - `GET /categorias` — lista categorias ordenadas por nome
  - `GET /transacoes?categoria=<nome ou id>` — filtra transações por categoria (aceita ID numérico ou nome)
- **Relacionamento**: `categoria_id` em transações (INTEGER NULL REFERENCES categorias(id))
- **Migração**: coluna `categoria_id` adicionada via ALTER TABLE se não existir (compatibilidade com transações antigas)
- **Índices**: `idx_transacoes_data` (DESC), `idx_transacoes_categoria_id`

### Aula 4 - Saldo e Resumo Mensal
- **Models**: SaldoResponse, ResumoCategoria, ResumoResponse (Decimal com 2 casas decimais)
- **Endpoints**:
  - `GET /saldo` — retorna `{ entradas, saidas, saldo }` de todas as transações
  - `GET /resumo?mes=YYYY-MM` — retorna `{ mes, entradas, saidas, saldo, por_categoria: [{categoria, total}] }`
- **Queries SQL (agregações, sem loops Python)**:
  - **Saldo total**: `SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END)` e `SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END)` com `COALESCE(..., 0)`
  - **Resumo mensal**: filtro `strftime('%Y-%m', data) = ?` + mesma agregação condicional
  - **Por categoria**: `LEFT JOIN categorias` + `GROUP BY c.nome` + `COALESCE(c.nome, 'Sem categoria')` — apenas saídas (`tipo='saida'`)
- **Validação de `mes`**: regex `^\d{4}-\d{2}$` + verificação 01-12; retorna 422 se inválido
- **Arredondamento**: `Decimal.quantize(Decimal("0.01"))` em todos os valores monetários
- **Mês sem dados**: retorna zeros e `por_categoria: []` (HTTP 200)

### Convenções de API
- Datas no formato ISO `YYYY-MM-DD` (serializadas via `date.isoformat()`)
- Valores monetários: `Decimal` com 2 casas decimais no modelo, `float` no SQLite
- `tipo` restrito a `"entrada"` ou `"saida"` (CHECK constraint no banco + Literal no Pydantic)
- Erros de validação: HTTP 422 com formato padrão do FastAPI/Pydantic (`detail` array com objetos de erro); **não** usa formato custom `{ "erro": "..." }`

### Decisões de Design — Categorias (Aula 3+)
- **Categoria em transação: OPCIONAL** (`categoria_id INTEGER NULL REFERENCES categorias(id)`). Usuário pode lançar sem categorizar; evita atrito no uso inicial.
- **Filtrar por categoria inexistente: retorna lista vazia (HTTP 200)**. Filtro é query param, não recurso; sem match → `[]` + 200. `GET /categorias/{id}` inexistente continua 404.
- **Validação de categoria_id em transação**: retorna 422 se categoria_id fornecido não existir (verificação em `_validar_categoria_id`)

### Como Rodar
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Endpoints Implementados
- `POST /transacoes` — cria transação, retorna 201 com objeto (inclui `id`)
- `GET /transacoes` — lista todas ordenadas por `data DESC`
- `PUT /transacoes/{id}` — atualiza transação, retorna 200 com objeto atualizado
- `DELETE /transacoes/{id}` — exclui transação, retorna 204
- `POST /categorias` — cria categoria, retorna 201 com objeto (inclui `id`)
- `GET /categorias` — lista categorias ordenadas por nome
- `GET /transacoes?categoria=<nome ou id>` — filtra por categoria (nome ou ID)
- `GET /saldo` — retorna `{ entradas, saidas, saldo }` de todas as transações
- `GET /resumo?mes=YYYY-MM` — retorna `{ mes, entradas, saidas, saldo, por_categoria: [{categoria, total}] }`