"""Rotas para saldo e resumo mensal."""
import re
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, status
from database import get_connection
from models import SaldoResponse, ResumoResponse, ResumoCategoria

router = APIRouter(tags=["saldo"])


def _validar_mes(mes: str) -> None:
    """Valida formato YYYY-MM e se o mês é válido (01-12)."""
    if not re.match(r"^\d{4}-\d{2}$", mes):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Parâmetro 'mes' deve estar no formato YYYY-MM"
        )
    ano, mes_num = mes.split("-")
    mes_int = int(mes_num)
    if mes_int < 1 or mes_int > 12:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Mês inválido: deve ser entre 01 e 12"
        )


def _decimal_round(valor) -> Decimal:
    """Converte valor para Decimal com 2 casas decimais."""
    if valor is None:
        return Decimal("0.00")
    return Decimal(str(valor)).quantize(Decimal("0.01"))


@router.get("/saldo", response_model=SaldoResponse)
def obter_saldo() -> SaldoResponse:
    """Retorna o saldo total: entradas, saídas e saldo (entradas - saídas)."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) as saidas
            FROM transacoes
        """).fetchone()

        entradas = _decimal_round(row["entradas"])
        saidas = _decimal_round(row["saidas"])
        saldo = entradas - saidas

        return SaldoResponse(entradas=entradas, saidas=saidas, saldo=saldo)


@router.get("/resumo", response_model=ResumoResponse)
def obter_resumo_mensal(mes: str = Query(..., description="Mês no formato YYYY-MM")) -> ResumoResponse:
    """Retorna resumo do mês: entradas, saídas, saldo e quebra por categoria."""
    _validar_mes(mes)

    with get_connection() as conn:
        # Totais do mês
        row = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) as saidas
            FROM transacoes
            WHERE strftime('%Y-%m', data) = ?
        """, (mes,)).fetchone()

        entradas = _decimal_round(row["entradas"])
        saidas = _decimal_round(row["saidas"])
        saldo = entradas - saidas

        # Quebra por categoria (apenas saídas/despesas)
        rows = conn.execute("""
            SELECT
                COALESCE(c.nome, 'Sem categoria') as categoria,
                COALESCE(SUM(t.valor), 0) as total
            FROM transacoes t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE strftime('%Y-%m', t.data) = ? AND t.tipo = 'saida'
            GROUP BY c.nome
            ORDER BY total DESC
        """, (mes,)).fetchall()

        por_categoria = [
            ResumoCategoria(categoria=row["categoria"], total=_decimal_round(row["total"]))
            for row in rows
        ]

        return ResumoResponse(
            mes=mes,
            entradas=entradas,
            saidas=saidas,
            saldo=saldo,
            por_categoria=por_categoria
        )