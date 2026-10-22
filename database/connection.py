"""Conexão e inicialização do banco SQLite."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "transacoes.db"


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão SQLite com row_factory para acesso por nome de coluna."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Cria a tabela transacoes se não existir."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida'))
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data DESC)
        """)
        conn.commit()