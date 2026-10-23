"""Rotas para transações."""
import sqlite3
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, status
from database import get_connection
from models import TransacaoCreate, TransacaoResponse

router = APIRouter(prefix="/transacoes", tags=["transacoes"])


def _validar_categoria_id(conn, categoria_id: int | None) -> None:
    """Valida se o categoria_id existe. Lança 422 se inválido."""
    if categoria_id is not None:
        row = conn.execute(
            "SELECT id FROM categorias WHERE id = ?",
            (categoria_id,)
        ).fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Categoria não encontrada"
            )


def _row_para_response(row: sqlite3.Row) -> TransacaoResponse:
    """Converte row do banco para TransacaoResponse."""
    return TransacaoResponse(
        id=row["id"],
        data=row["data"],
        descricao=row["descricao"],
        valor=row["valor"],
        tipo=row["tipo"],
        categoria_id=row["categoria_id"]
    )


@router.post("", response_model=TransacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_transacao(transacao: TransacaoCreate) -> TransacaoResponse:
    """Registra uma nova transação."""
    with get_connection() as conn:
        _validar_categoria_id(conn, transacao.categoria_id)

        cursor = conn.execute(
            """
            INSERT INTO transacoes (data, descricao, valor, tipo, categoria_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (transacao.data.isoformat(), transacao.descricao, float(transacao.valor), transacao.tipo, transacao.categoria_id)
        )
        conn.commit()
        transacao_id = cursor.lastrowid

        row = conn.execute(
            "SELECT id, data, descricao, valor, tipo, categoria_id FROM transacoes WHERE id = ?",
            (transacao_id,)
        ).fetchone()

        return _row_para_response(row)


@router.get("", response_model=list[TransacaoResponse])
def listar_transacoes(
    categoria: str | None = Query(default=None, description="Filtrar por nome ou ID da categoria"),
    data_inicio: date | None = Query(default=None, description="Data inicial no formato YYYY-MM-DD"),
    data_fim: date | None = Query(default=None, description="Data final no formato YYYY-MM-DD"),
    valor_min: Decimal | None = Query(default=None, description="Valor mínimo", ge=0),
    valor_max: Decimal | None = Query(default=None, description="Valor máximo", ge=0),
) -> list[TransacaoResponse]:
    """Lista todas as transações, mais recentes primeiro. Opcionalmente filtra por categoria, período e faixa de valor."""
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

    with get_connection() as conn:
        # Construir query dinamicamente
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
            SELECT t.id, t.data, t.descricao, t.valor, t.tipo, t.categoria_id
            FROM transacoes t
        """

        # Se filtra por categoria nome, precisa do JOIN
        if categoria is not None and not categoria.isdigit():
            base_query = base_query.replace("FROM transacoes t", "FROM transacoes t JOIN categorias c ON t.categoria_id = c.id")

        if where_clauses:
            query = base_query + " WHERE " + " AND ".join(where_clauses) + " ORDER BY t.data DESC"
        else:
            query = base_query + " ORDER BY t.data DESC"

        rows = conn.execute(query, params).fetchall()

        return [_row_para_response(row) for row in rows]


@router.put("/{transacao_id}", response_model=TransacaoResponse)
def atualizar_transacao(transacao_id: int, transacao: TransacaoCreate) -> TransacaoResponse:
    """Atualiza uma transação existente."""
    with get_connection() as conn:
        _validar_categoria_id(conn, transacao.categoria_id)

        # Verifica se a transação existe
        row = conn.execute(
            "SELECT id FROM transacoes WHERE id = ?",
            (transacao_id,)
        ).fetchone()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada")

        # Atualiza a transação
        conn.execute(
            """
            UPDATE transacoes
            SET data = ?, descricao = ?, valor = ?, tipo = ?, categoria_id = ?
            WHERE id = ?
            """,
            (transacao.data.isoformat(), transacao.descricao, float(transacao.valor), transacao.tipo, transacao.categoria_id, transacao_id)
        )
        conn.commit()

        # Busca a transação atualizada para retornar
        row = conn.execute(
            "SELECT id, data, descricao, valor, tipo, categoria_id FROM transacoes WHERE id = ?",
            (transacao_id,)
        ).fetchone()

        return _row_para_response(row)


@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_transacao(transacao_id: int) -> None:
    """Exclui uma transação."""
    with get_connection() as conn:
        # Verifica se a transação existe
        row = conn.execute(
            "SELECT id FROM transacoes WHERE id = ?",
            (transacao_id,)
        ).fetchone()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada")

        # Exclui a transação
        conn.execute(
            "DELETE FROM transacoes WHERE id = ?",
            (transacao_id,)
        )
        conn.commit()