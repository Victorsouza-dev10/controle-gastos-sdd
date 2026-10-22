"""Rotas para transações."""
from fastapi import APIRouter, HTTPException, status
from database import get_connection
from models import TransacaoCreate, TransacaoResponse

router = APIRouter(prefix="/transacoes", tags=["transacoes"])


@router.post("", response_model=TransacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_transacao(transacao: TransacaoCreate) -> TransacaoResponse:
    """Registra uma nova transação."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO transacoes (data, descricao, valor, tipo)
            VALUES (?, ?, ?, ?)
            """,
            (transacao.data.isoformat(), transacao.descricao, float(transacao.valor), transacao.tipo)
        )
        conn.commit()
        transacao_id = cursor.lastrowid

        # Busca a transação criada para retornar com o id
        row = conn.execute(
            "SELECT id, data, descricao, valor, tipo FROM transacoes WHERE id = ?",
            (transacao_id,)
        ).fetchone()

        return TransacaoResponse(
            id=row["id"],
            data=row["data"],
            descricao=row["descricao"],
            valor=row["valor"],
            tipo=row["tipo"]
        )


@router.get("", response_model=list[TransacaoResponse])
def listar_transacoes() -> list[TransacaoResponse]:
    """Lista todas as transações, mais recentes primeiro."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, data, descricao, valor, tipo FROM transacoes ORDER BY data DESC"
        ).fetchall()

        return [
            TransacaoResponse(
                id=row["id"],
                data=row["data"],
                descricao=row["descricao"],
                valor=row["valor"],
                tipo=row["tipo"]
            )
            for row in rows
        ]