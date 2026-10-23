"""Testes para CRUD e filtros de transações."""
from decimal import Decimal
from datetime import date
from fastapi.testclient import TestClient


class TestTransacoesCRUD:
    """Testes de CRUD básico de transações."""

    def test_criar_transacao_valida(self, client: TestClient):
        """Criar transação válida retorna 201 com objeto incluindo id."""
        payload = {
            "data": "2026-10-15",
            "descricao": "Salário",
            "valor": "5000.00",
            "tipo": "entrada"
        }
        response = client.post("/transacoes", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["data"] == "2026-10-15"
        assert data["descricao"] == "Salário"
        assert Decimal(data["valor"]) == Decimal("5000.00")
        assert data["tipo"] == "entrada"
        assert data["categoria_id"] is None

    def test_criar_transacao_com_categoria(self, client: TestClient):
        """Criar transação com categoria_id válido."""
        # Criar categoria primeiro
        cat_response = client.post("/categorias", json={"nome": "alimentacao"})
        assert cat_response.status_code == 201
        cat_id = cat_response.json()["id"]

        payload = {
            "data": "2026-10-15",
            "descricao": "Supermercado",
            "valor": "150.00",
            "tipo": "saida",
            "categoria_id": cat_id
        }
        response = client.post("/transacoes", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["categoria_id"] == cat_id

    def test_criar_transacao_valor_invalido(self, client: TestClient):
        """Criar transação com valor <= 0 retorna 422."""
        payload = {
            "data": "2026-10-15",
            "descricao": "Teste",
            "valor": "0",
            "tipo": "entrada"
        }
        response = client.post("/transacoes", json=payload)
        assert response.status_code == 422

    def test_criar_transacao_tipo_invalido(self, client: TestClient):
        """Criar transação com tipo inválido retorna 422."""
        payload = {
            "data": "2026-10-15",
            "descricao": "Teste",
            "valor": "100.00",
            "tipo": "invalido"
        }
        response = client.post("/transacoes", json=payload)
        assert response.status_code == 422

    def test_criar_transacao_data_malformada(self, client: TestClient):
        """Criar transação com data malformada retorna 422."""
        payload = {
            "data": "15-10-2026",
            "descricao": "Teste",
            "valor": "100.00",
            "tipo": "entrada"
        }
        response = client.post("/transacoes", json=payload)
        assert response.status_code == 422

    def test_criar_transacao_descricao_vazia(self, client: TestClient):
        """Criar transação com descrição vazia retorna 422."""
        payload = {
            "data": "2026-10-15",
            "descricao": "",
            "valor": "100.00",
            "tipo": "entrada"
        }
        response = client.post("/transacoes", json=payload)
        assert response.status_code == 422

    def test_listar_transacoes_ordenadas_por_data_desc(self, client: TestClient):
        """Listar transações retorna ordenadas por data DESC."""
        # Criar transações em datas diferentes
        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "A", "valor": "100", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-20", "descricao": "B", "valor": "200", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-15", "descricao": "C", "valor": "300", "tipo": "entrada"})

        response = client.get("/transacoes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        # Verificar ordenação DESC (mais recente primeiro)
        datas = [t["data"] for t in data[:3]]
        assert datas == ["2026-10-20", "2026-10-15", "2026-10-10"]

    def test_atualizar_transacao(self, client: TestClient):
        """Atualizar transação existente retorna 200 com objeto atualizado."""
        # Criar
        create_resp = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "Original", "valor": "100", "tipo": "entrada"
        })
        transacao_id = create_resp.json()["id"]

        # Atualizar
        update_resp = client.put(f"/transacoes/{transacao_id}", json={
            "data": "2026-10-16", "descricao": "Atualizado", "valor": "200", "tipo": "saida"
        })
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["id"] == transacao_id
        assert data["data"] == "2026-10-16"
        assert data["descricao"] == "Atualizado"
        assert Decimal(data["valor"]) == Decimal("200.00")
        assert data["tipo"] == "saida"

    def test_atualizar_transacao_inexistente(self, client: TestClient):
        """Atualizar transação inexistente retorna 404."""
        response = client.put("/transacoes/99999", json={
            "data": "2026-10-15", "descricao": "Teste", "valor": "100", "tipo": "entrada"
        })
        assert response.status_code == 404

    def test_excluir_transacao(self, client: TestClient):
        """Excluir transação retorna 204."""
        create_resp = client.post("/transacoes", json={
            "data": "2026-10-15", "descricao": "Para excluir", "valor": "100", "tipo": "entrada"
        })
        transacao_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/transacoes/{transacao_id}")
        assert delete_resp.status_code == 204

        # Verificar que não existe mais (listar e confirmar que não está na lista)
        get_resp = client.get("/transacoes")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert not any(t["id"] == transacao_id for t in data)

    def test_excluir_transacao_inexistente(self, client: TestClient):
        """Excluir transação inexistente retorna 404."""
        response = client.delete("/transacoes/99999")
        assert response.status_code == 404


class TestTransacoesFiltros:
    """Testes de filtros avançados de transações."""

    def test_filtrar_por_categoria_nome(self, client: TestClient, db_conn):
        """Filtrar por categoria usando nome."""
        # Setup: criar categoria e transações
        cat_resp = client.post("/categorias", json={"nome": "transporte"})
        cat_id = cat_resp.json()["id"]

        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "Uber", "valor": "50", "tipo": "saida", "categoria_id": cat_id})
        client.post("/transacoes", json={"data": "2026-10-11", "descricao": "Ônibus", "valor": "10", "tipo": "saida", "categoria_id": cat_id})
        client.post("/transacoes", json={"data": "2026-10-12", "descricao": "Salário", "valor": "5000", "tipo": "entrada"})  # sem categoria

        response = client.get("/transacoes?categoria=transporte")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(t["categoria_id"] == cat_id for t in data)

    def test_filtrar_por_categoria_id(self, client: TestClient, db_conn):
        """Filtrar por categoria usando ID numérico."""
        cat_resp = client.post("/categorias", json={"nome": "lazer"})
        cat_id = cat_resp.json()["id"]

        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "Cinema", "valor": "50", "tipo": "saida", "categoria_id": cat_id})
        client.post("/transacoes", json={"data": "2026-10-11", "descricao": "Jantar", "valor": "100", "tipo": "saida"})  # sem categoria

        response = client.get(f"/transacoes?categoria={cat_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["categoria_id"] == cat_id

    def test_filtrar_por_data_inicio(self, client: TestClient, db_conn):
        """Filtrar por data_inicio."""
        client.post("/transacoes", json={"data": "2026-10-01", "descricao": "Antiga", "valor": "100", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-15", "descricao": "Recente", "valor": "200", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-20", "descricao": "Mais recente", "valor": "300", "tipo": "entrada"})

        response = client.get("/transacoes?data_inicio=2026-10-15")
        assert response.status_code == 200
        data = response.json()
        datas = [t["data"] for t in data]
        assert all(d >= "2026-10-15" for d in datas)

    def test_filtrar_por_data_fim(self, client: TestClient, db_conn):
        """Filtrar por data_fim."""
        client.post("/transacoes", json={"data": "2026-10-01", "descricao": "Antiga", "valor": "100", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-15", "descricao": "Meio", "valor": "200", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-20", "descricao": "Recente", "valor": "300", "tipo": "entrada"})

        response = client.get("/transacoes?data_fim=2026-10-15")
        assert response.status_code == 200
        data = response.json()
        datas = [t["data"] for t in data]
        assert all(d <= "2026-10-15" for d in datas)

    def test_filtrar_por_periodo_completo(self, client: TestClient, db_conn):
        """Filtrar por data_inicio e data_fim juntos."""
        client.post("/transacoes", json={"data": "2026-09-30", "descricao": "Fora antes", "valor": "100", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-01", "descricao": "Início", "valor": "200", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-15", "descricao": "Meio", "valor": "300", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-31", "descricao": "Fim", "valor": "400", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-11-01", "descricao": "Fora depois", "valor": "500", "tipo": "entrada"})

        response = client.get("/transacoes?data_inicio=2026-10-01&data_fim=2026-10-31")
        assert response.status_code == 200
        data = response.json()
        datas = [t["data"] for t in data]
        assert len(data) == 3
        assert all("2026-10-" in d for d in datas)

    def test_filtrar_por_valor_min(self, client: TestClient, db_conn):
        """Filtrar por valor_min."""
        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "Pequeno", "valor": "10", "tipo": "saida"})
        client.post("/transacoes", json={"data": "2026-10-11", "descricao": "Médio", "valor": "100", "tipo": "saida"})
        client.post("/transacoes", json={"data": "2026-10-12", "descricao": "Grande", "valor": "1000", "tipo": "saida"})

        response = client.get("/transacoes?valor_min=100")
        assert response.status_code == 200
        data = response.json()
        assert all(Decimal(t["valor"]) >= Decimal("100") for t in data)

    def test_filtrar_por_valor_max(self, client: TestClient, db_conn):
        """Filtrar por valor_max."""
        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "Pequeno", "valor": "10", "tipo": "saida"})
        client.post("/transacoes", json={"data": "2026-10-11", "descricao": "Médio", "valor": "100", "tipo": "saida"})
        client.post("/transacoes", json={"data": "2026-10-12", "descricao": "Grande", "valor": "1000", "tipo": "saida"})

        response = client.get("/transacoes?valor_max=100")
        assert response.status_code == 200
        data = response.json()
        assert all(Decimal(t["valor"]) <= Decimal("100") for t in data)

    def test_filtrar_por_faixa_valor(self, client: TestClient, db_conn):
        """Filtrar por valor_min e valor_max juntos."""
        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "Pequeno", "valor": "10", "tipo": "saida"})
        client.post("/transacoes", json={"data": "2026-10-11", "descricao": "Médio", "valor": "100", "tipo": "saida"})
        client.post("/transacoes", json={"data": "2026-10-12", "descricao": "Grande", "valor": "1000", "tipo": "saida"})

        response = client.get("/transacoes?valor_min=50&valor_max=500")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert Decimal(data[0]["valor"]) == Decimal("100")

    def test_filtrar_combinado_categoria_periodo_valor(self, client: TestClient, db_conn):
        """Filtrar combinado: categoria + período + faixa de valor."""
        # Criar categorias
        cat_transporte = client.post("/categorias", json={"nome": "transporte"}).json()["id"]
        cat_alimentacao = client.post("/categorias", json={"nome": "alimentacao"}).json()["id"]

        # Transações de transporte no período com valores variados
        client.post("/transacoes", json={"data": "2026-10-01", "descricao": "Uber barato", "valor": "20", "tipo": "saida", "categoria_id": cat_transporte})
        client.post("/transacoes", json={"data": "2026-10-15", "descricao": "Uber médio", "valor": "50", "tipo": "saida", "categoria_id": cat_transporte})
        client.post("/transacoes", json={"data": "2026-10-31", "descricao": "Uber caro", "valor": "200", "tipo": "saida", "categoria_id": cat_transporte})

        # Transação de alimentação no mesmo período (não deve aparecer)
        client.post("/transacoes", json={"data": "2026-10-15", "descricao": "Restaurante", "valor": "100", "tipo": "saida", "categoria_id": cat_alimentacao})

        # Transação fora do período (não deve aparecer)
        client.post("/transacoes", json={"data": "2026-09-15", "descricao": "Uber antigo", "valor": "50", "tipo": "saida", "categoria_id": cat_transporte})

        # Filtrar: categoria=transporte + data_inicio=2026-10-01 + data_fim=2026-10-31 + valor_min=30 + valor_max=100
        response = client.get(
            f"/transacoes?categoria=transporte&data_inicio=2026-10-01&data_fim=2026-10-31&valor_min=30&valor_max=100"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["descricao"] == "Uber médio"
        assert Decimal(data[0]["valor"]) == Decimal("50.00")
        assert data[0]["categoria_id"] == cat_transporte