"""Routes package."""
from .transacoes import router as transacoes_router
from .categorias import router as categorias_router
from .saldo import router as saldo_router

__all__ = ["transacoes_router", "categorias_router", "saldo_router"]