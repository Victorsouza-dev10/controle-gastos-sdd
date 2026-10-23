"""Configuração de testes com banco de dados temporário."""
import tempfile
import sqlite3
from pathlib import Path
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_db_path():
    """Cria um banco de dados temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup - ignore PermissionError on Windows (file may still be locked)
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass  # Windows may keep file locked; will be cleaned up on reboot


def _init_test_db(db_path: Path):
    """Inicializa o schema no banco de teste."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Criar tabelas
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)
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

    # Migração: adicionar categoria_id se não existir
    try:
        conn.execute("SELECT categoria_id FROM transacoes LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE transacoes ADD COLUMN categoria_id INTEGER NULL")

    # Índices
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_categoria_id ON transacoes(categoria_id)")

    conn.commit()
    conn.close()


@pytest.fixture(scope="function")
def test_app(test_db_path):
    """Cria uma instância da app FastAPI com override da conexão do banco.

    Importante: o banco é inicializado ANTES de importar main, para que
    o startup event use o banco de teste.
    """
    # Inicializar o banco de teste ANTES de importar a app
    _init_test_db(test_db_path)

    # Configurar DATABASE_URL para o banco de teste ANTES de importar config/main
    import os
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

    # Invalidar cache do módulo config para recarregar settings
    import config
    import importlib
    importlib.reload(config)

    # Patch do DB_PATH no database.connection (para compatibilidade com código legado)
    import database.connection as db_conn_module
    original_db_path = db_conn_module.DB_PATH
    db_conn_module.DB_PATH = test_db_path

    # Importar a app (agora init_db usará o test_db_path no startup event)
    from main import app

    # Override da conexão para usar o banco de teste
    from database import get_connection as original_get_connection

    def override_get_connection():
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    app.dependency_overrides[original_get_connection] = override_get_connection
    yield app

    # Cleanup: restaurar DB_PATH original e limpar overrides
    app.dependency_overrides.clear()
    db_conn_module.DB_PATH = original_db_path


@pytest.fixture(scope="function", autouse=True)
def cleanup_db(test_db_path):
    """Limpa o banco de dados após cada teste automaticamente."""
    yield
    # Limpar dados após cada teste
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("DELETE FROM transacoes")
    conn.execute("DELETE FROM categorias")
    conn.commit()
    conn.close()


@pytest.fixture(scope="function")
def client(test_app):
    """TestClient do FastAPI para testes de integração."""
    return TestClient(test_app)


@pytest.fixture(scope="function")
def db_conn(test_db_path):
    """Conexão direta ao banco de teste para setup/teardown de dados (para testes que precisam manipular o DB diretamente)."""
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()