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
    """Cria as tabelas categorias e transacoes se não existirem."""
    with get_connection() as conn:
        # Tabela categorias
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        """)

        # Tabela transacoes (versão completa com categoria_id)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
                categoria_id INTEGER NULL REFERENCES categorias(id)
            )
        """)

        # Migração: verificar se a coluna categoria_id existe na tabela transacoes
        # (SQLite não suporta ALTER TABLE ... ADD COLUMN com REFERENCES)
        # Precisamos fazer isso ANTES de criar o índice
        try:
            # Tenta consultar a coluna - se falhar, a coluna não existe
            conn.execute("SELECT categoria_id FROM transacoes LIMIT 1")
        except sqlite3.OperationalError:
            # Coluna não existe, adicionar sem REFERENCES (a FK será apenas lógica)
            conn.execute("ALTER TABLE transacoes ADD COLUMN categoria_id INTEGER NULL")

        # Índices (agora a coluna já existe)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transacoes_categoria_id ON transacoes(categoria_id)
        """)

        conn.commit()