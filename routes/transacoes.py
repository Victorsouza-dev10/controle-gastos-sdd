"""Rotas para transações."""
import sqlite3
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
def listar_transacoes(categoria: str | None = Query(default=None, description="Filtrar por nome ou ID da categoria")) -> list[TransacaoResponse]:
    """Lista todas as transações, mais recentes primeiro. Opcionalmente filtra por categoria."""
    with get_connection() as conn:
        if categoria is not None:
            # Tenta interpretar como ID primeiro, senão como nome
            try:
                cat_id = int(categoria)
                rows = conn.execute(
                    """
                    SELECT t.id, t.data, t.descricao, t.valor, t.tipo, t.categoria_id
                    FROM transacoes t
                    WHERE t.categoria_id = ?
                    ORDER BY t.data DESC
                    """,
                    (cat_id,)
                ).fetchall()
            except ValueError:
                # É um nome
                rows = conn.execute(
                    """
                    SELECT t.id, t.data, t.descricao, t.valor, t.tipo, t.categoria_id
                    FROM transacoes t
                    JOIN categorias c ON t.categoria_id = c.id
                    WHERE c.nome = ?
                    ORDER BY t.data DESC
                    """,
                    (categoria,)
                ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, data, descricao, valor, tipo, categoria_id FROM transacoes ORDER BY data DESC"
            ).fetchall()

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