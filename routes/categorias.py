"""Rotas para categorias."""
import sqlite3
from fastapi import APIRouter, HTTPException, status
from database import get_connection
from models import CategoriaCreate, CategoriaResponse

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(categoria: CategoriaCreate) -> CategoriaResponse:
    """Cria uma nova categoria."""
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO categorias (nome) VALUES (?)",
                (categoria.nome,)
            )
            conn.commit()
            categoria_id = cursor.lastrowid

            row = conn.execute(
                "SELECT id, nome FROM categorias WHERE id = ?",
                (categoria_id,)
            ).fetchone()

            return CategoriaResponse(id=row["id"], nome=row["nome"])
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Categoria com este nome já existe"
            )


@router.get("", response_model=list[CategoriaResponse])
def listar_categorias() -> list[CategoriaResponse]:
    """Lista todas as categorias ordenadas por nome."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, nome FROM categorias ORDER BY nome"
        ).fetchall()

        return [
            CategoriaResponse(id=row["id"], nome=row["nome"])
            for row in rows
        ]