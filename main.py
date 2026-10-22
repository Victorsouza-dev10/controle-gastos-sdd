"""Entry point da aplicação FastAPI."""
from fastapi import FastAPI
from database import init_db
from routes import transacoes_router, categorias_router

app = FastAPI(title="Controle de Gastos Pessoais")


@app.on_event("startup")
def startup() -> None:
    """Inicializa o banco de dados na partida."""
    init_db()


app.include_router(transacoes_router)
app.include_router(categorias_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)