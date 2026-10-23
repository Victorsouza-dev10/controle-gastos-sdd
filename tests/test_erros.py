"""Testes de validação e casos de erro (422, 404)."""
from fastapi.testclient import TestClient


class TestErrosValidacaoTransacoes:
    """Testes de erros de validação em transações."""

    def test_criar_transacao_valor_zero(self, client: TestClient):
        """Valor = 0 retorna 422."""
        response = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "Teste", "valor": "0", "tipo": "entrada"
        })
        assert response.status_code == 422

    def test_criar_transacao_valor_negativo(self, client: TestClient):
        """Valor negativo retorna 422."""
        response = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "Teste", "valor": "-100", "tipo": "entrada"
        })
        assert response.status_code == 422

    def test_criar_transacao_tipo_invalido(self, client: TestClient):
        """Tipo inválido retorna 422."""
        response = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "Teste", "valor": "100", "tipo": "investimento"
        })
        assert response.status_code == 422

    def test_criar_transacao_data_malformada(self, client: TestClient):
        """Data em formato errado retorna 422."""
        response = client.post("/transacoes", json={
            "data": "15/10/2026", "descricao": "Teste", "valor": "100", "tipo": "entrada"
        })
        assert response.status_code == 422

    def test_criar_transacao_descricao_vazia(self, client: TestClient):
        """Descrição vazia retorna 422."""
        response = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "", "valor": "100", "tipo": "entrada"
        })
        assert response.status_code == 422

    def test_criar_transacao_descricao_muito_longa(self, client: TestClient):
        """Descrição > 200 chars retorna 422."""
        response = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "x" * 201, "valor": "100", "tipo": "entrada"
        })
        assert response.status_code == 422


class TestErrosValidacaoFiltros:
    """Testes de erros de validação nos filtros de listagem."""

    def test_filtro_data_inicio_maior_que_data_fim(self, client: TestClient):
        """data_inicio > data_fim retorna 422."""
        response = client.get("/transacoes?data_inicio=2026-10-20&data_fim=2026-10-10")
        assert response.status_code == 422
        assert "data_inicio não pode ser maior que data_fim" in response.json()["detail"]

    def test_filtro_valor_min_maior_que_valor_max(self, client: TestClient):
        """valor_min > valor_max retorna 422."""
        response = client.get("/transacoes?valor_min=500&valor_max=100")
        assert response.status_code == 422
        assert "valor_min não pode ser maior que valor_max" in response.json()["detail"]

    def test_filtro_data_malformada(self, client: TestClient):
        """Data malformada no filtro retorna 422."""
        response = client.get("/transacoes?data_inicio=15-10-2026")
        assert response.status_code == 422


class TestErros404:
    """Testes de erros 404 (recurso não encontrado)."""

    def test_get_transacao_inexistente(self, client: TestClient):
        """GET /transacoes/{id} inexistente retorna 404."""
        # Note: não existe endpoint GET /transacoes/{id}, mas PUT e DELETE têm
        response = client.put("/transacoes/99999", json={
            "data": "2026-10-15", "descricao": "Teste", "valor": "100", "tipo": "entrada"
        })
        assert response.status_code == 404

    def test_delete_transacao_inexistente(self, client: TestClient):
        """DELETE /transacoes/{id} inexistente retorna 404."""
        response = client.delete("/transacoes/99999")
        assert response.status_code == 404

    def test_put_transacao_inexistente(self, client: TestClient):
        """PUT /transacoes/{id} inexistente retorna 404."""
        response = client.put("/transacoes/99999", json={
            "data": "2026-10-15", "descricao": "Teste", "valor": "100", "tipo": "entrada"
        })
        assert response.status_code == 404

    def test_categoria_inexistente_em_transacao(self, client: TestClient):
        """Usar categoria_id inexistente em transação retorna 422."""
        response = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "Teste", "valor": "100", "tipo": "entrada", "categoria_id": 99999
        })
        assert response.status_code == 422
        assert "Categoria não encontrada" in response.json()["detail"]


class TestErrosCategorias:
    """Testes de erros em categorias."""

    def test_criar_categoria_nome_duplicado(self, client: TestClient):
        """Criar categoria com nome duplicado retorna 422."""
        client.post("/categorias", json={"nome": "duplicada"})
        response = client.post("/categorias", json={"nome": "duplicada"})
        assert response.status_code == 422

    def test_criar_categoria_nome_vazio(self, client: TestClient):
        """Criar categoria com nome vazio retorna 422."""
        response = client.post("/categorias", json={"nome": ""})
        assert response.status_code == 422

    def test_criar_categoria_nome_muito_longo(self, client: TestClient):
        """Criar categoria com nome > 100 chars retorna 422."""
        response = client.post("/categorias", json={"nome": "x" * 101})
        assert response.status_code == 422