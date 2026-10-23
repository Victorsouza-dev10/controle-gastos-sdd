"""Testes para CRUD de categorias."""
from fastapi.testclient import TestClient


class TestCategoriasCRUD:
    """Testes de CRUD de categorias."""

    def test_criar_categoria_valida(self, client: TestClient):
        """Criar categoria válida retorna 201 com objeto incluindo id."""
        payload = {"nome": "alimentacao"}
        response = client.post("/categorias", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["nome"] == "alimentacao"

    def test_criar_categoria_duplicada(self, client: TestClient):
        """Criar categoria com nome duplicado retorna 422."""
        payload = {"nome": "transporte"}
        client.post("/categorias", json=payload)  # Primeira criação
        response = client.post("/categorias", json=payload)  # Duplicada
        assert response.status_code == 422

    def test_listar_categorias_ordenadas_por_nome(self, client: TestClient):
        """Listar categorias retorna ordenadas por nome."""
        client.post("/categorias", json={"nome": "zebra"})
        client.post("/categorias", json={"nome": "alpha"})
        client.post("/categorias", json={"nome": "beta"})

        response = client.get("/categorias")
        assert response.status_code == 200
        data = response.json()
        nomes = [c["nome"] for c in data]
        assert nomes == ["alpha", "beta", "zebra"]