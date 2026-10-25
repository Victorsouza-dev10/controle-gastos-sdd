# Controle de Gastos Pessoais

API REST para controle de gastos pessoais com dashboard (entradas, saídas, saldo e gastos por categoria).

## Funcionalidades

- **Transações**: CRUD completo com validação
- **Categorias**: Gerenciamento de categorias
- **Filtros**: Por categoria, período (data início/fim), faixa de valor
- **Saldo e Resumo**: Saldo total e resumo mensal por categoria
- **Exportação CSV**: Extrato com mesmos filtros da listagem
- **Dashboard Web**: Gráfico de gastos por categoria (Chart.js) e cards de saldo

## Tecnologias

- **FastAPI** - Framework web
- **SQLite** - Banco de dados (biblioteca padrão `sqlite3`)
- **Pydantic v2** - Validação e configuração via variáveis de ambiente
- **Uvicorn** - Servidor ASGI
- **Chart.js** - Gráficos no dashboard (via CDN)

## Estrutura de Pastas

```
aula1/
├── config.py              # Configurações (pydantic-settings)
├── main.py                # Entry point
├── requirements.txt       # Dependências
├── database/connection.py # Conexão e init do SQLite
├── models/schemas.py      # Models Pydantic
├── routes/                # Endpoints da API
│   ├── transacoes.py
│   ├── categorias.py
│   ├── saldo.py
│   └── export_dashboard.py
├── static/                # Dashboard (HTML, CSS, JS)
├── tests/                 # Testes automatizados (pytest)
└── spec/                  # Especificações das aulas (SDD)
```

## Como Rodar (Windows)

### 1. Instalar dependências

```cmd
pip install -r requirements.txt
```

### 2. Subir o servidor

**Opção A: Arquivo .env (recomendado)**
```cmd
echo HOST=0.0.0.0 > .env
echo PORT=8000 >> .env
echo DEBUG=true >> .env
echo DATABASE_URL=sqlite:///./transacoes.db >> .env
uvicorn main:app
```

**Opção B: Variáveis inline (PowerShell)**
```powershell
$env:DEBUG="true"; uvicorn main:app
```

**Opção C: Variáveis inline (cmd.exe)**
```cmd
set DEBUG=true && uvicorn main:app
```

### 3. Acessar

- **API (Swagger)**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8000/

### Produção (PowerShell)

```powershell
$env:HOST="0.0.0.0"; $env:PORT="8080"; $env:DEBUG="false"; $env:DATABASE_URL="sqlite:///./prod.db"; uvicorn main:app
```

## Testes

```cmd
pytest tests/ -v
```

> Os testes usam banco temporário isolado - o banco de produção nunca é afetado.

## Como Este Projeto Foi Feito

- Projeto criado como exercício do curso de **Spec Driven Development (SDD)** com **Claude Code**.
- A maior parte do código foi gerada por IA (Claude Code) a partir de specs escritas por mim, que estão na pasta `spec/`.
- Meu papel: escrever as specs, revisar, testar e ajustar.
- Escrito de forma honesta e direta, sem exagerar nem diminuir.

## Autor

**Victor Souza** - [GitHub](https://github.com/Victorsouza-dev10)