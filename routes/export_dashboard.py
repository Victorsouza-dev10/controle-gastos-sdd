"""Rotas para exportação CSV e dashboard."""
import csv
import io
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, Response, status
from database import get_connection

router = APIRouter(tags=["export", "dashboard"])


def _build_transactions_query(
    categoria: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    valor_min: Decimal | None = None,
    valor_max: Decimal | None = None,
):
    """
    Constrói a query SQL e parâmetros para buscar transações com filtros.
    Retorna (query, params).
    """
    # Validações de período e faixa de valor
    if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="data_inicio não pode ser maior que data_fim"
        )
    if valor_min is not None and valor_max is not None and valor_min > valor_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="valor_min não pode ser maior que valor_max"
        )

    where_clauses = []
    params = []

    if categoria is not None:
        try:
            cat_id = int(categoria)
            where_clauses.append("t.categoria_id = ?")
            params.append(cat_id)
        except ValueError:
            where_clauses.append("c.nome = ?")
            params.append(categoria)

    if data_inicio is not None:
        where_clauses.append("t.data >= ?")
        params.append(data_inicio.isoformat())

    if data_fim is not None:
        where_clauses.append("t.data <= ?")
        params.append(data_fim.isoformat())

    if valor_min is not None:
        where_clauses.append("t.valor >= ?")
        params.append(float(valor_min))

    if valor_max is not None:
        where_clauses.append("t.valor <= ?")
        params.append(float(valor_max))

    # Montar query base
    base_query = """
        SELECT t.id, t.data, t.descricao, t.valor, t.tipo, t.categoria_id, c.nome as categoria_nome
        FROM transacoes t
    """

    # Se filtra por categoria nome, precisa do JOIN
    if categoria is not None and not categoria.isdigit():
        base_query = base_query.replace("FROM transacoes t", "FROM transacoes t JOIN categorias c ON t.categoria_id = c.id")
    else:
        # LEFT JOIN para incluir nome da categoria nos resultados
        base_query = base_query.replace("FROM transacoes t", "FROM transacoes t LEFT JOIN categorias c ON t.categoria_id = c.id")

    if where_clauses:
        query = base_query + " WHERE " + " AND ".join(where_clauses) + " ORDER BY t.data DESC"
    else:
        query = base_query + " ORDER BY t.data DESC"

    return query, params


@router.get("/export.csv")
def exportar_csv(
    categoria: str | None = Query(default=None, description="Filtrar por nome ou ID da categoria"),
    data_inicio: date | None = Query(default=None, description="Data inicial no formato YYYY-MM-DD"),
    data_fim: date | None = Query(default=None, description="Data final no formato YYYY-MM-DD"),
    valor_min: Decimal | None = Query(default=None, description="Valor mínimo", ge=0),
    valor_max: Decimal | None = Query(default=None, description="Valor máximo", ge=0),
) -> Response:
    """
    Exporta transações em formato CSV.
    Respeita os mesmos filtros do endpoint GET /transacoes.
    """
    query, params = _build_transactions_query(
        categoria=categoria,
        data_inicio=data_inicio,
        data_fim=data_fim,
        valor_min=valor_min,
        valor_max=valor_max,
    )

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    # Gerar CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)

    # Cabeçalho
    writer.writerow(["id", "data", "descricao", "valor", "tipo", "categoria_id", "categoria_nome"])

    # Dados
    for row in rows:
        writer.writerow([
            row["id"],
            row["data"],
            row["descricao"],
            f"{row['valor']:.2f}",
            row["tipo"],
            row["categoria_id"] if row["categoria_id"] is not None else "",
            row["categoria_nome"] if row["categoria_nome"] is not None else "",
        ])

    csv_content = output.getvalue()
    output.close()

    # Retornar como download
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=extrato.csv"
        }
    )


@router.get("/dashboard")
def dashboard() -> Response:
    """
    Serve o dashboard HTML estático.
    """
    # Ler o arquivo HTML
    import os
    html_path = os.path.join(os.path.dirname(__file__), "..", "static", "dashboard.html")
    html_path = os.path.abspath(html_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return Response(content=html_content, media_type="text/html; charset=utf-8")


@router.get("/")
def root() -> Response:
    """
    Redireciona para o dashboard.
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")