"""Testes para saldo e resumo mensal."""
from decimal import Decimal
from fastapi.testclient import TestClient


class TestSaldo:
    """Testes do endpoint GET /saldo."""

    def test_saldo_retorna_totais_corretos(self, client: TestClient, db_conn):
        """GET /saldo retorna entradas, saídas e saldo corretos."""
        # Criar transações de teste
        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "Salário", "valor": "5000", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-11", "descricao": "Freelance", "valor": "1000", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-12", "descricao": "Aluguel", "valor": "2000", "tipo": "saida"})
        client.post("/transacoes", json={"data": "2026-10-13", "descricao": "Supermercado", "valor": "500", "tipo": "saida"})

        response = client.get("/saldo")
        assert response.status_code == 200
        data = response.json()
        assert data["entradas"] == "6000.00"
        assert data["saidas"] == "2500.00"
        assert data["saldo"] == "3500.00"

    def test_saldo_sem_transacoes(self, client: TestClient, db_conn):
        """GET /saldo sem transações retorna zeros."""
        response = client.get("/saldo")
        assert response.status_code == 200
        data = response.json()
        assert data["entradas"] == "0.00"
        assert data["saidas"] == "0.00"
        assert data["saldo"] == "0.00"


class TestResumoMensal:
    """Testes do endpoint GET /resumo."""

    def test_resumo_mes_com_dados(self, client: TestClient, db_conn):
        """GET /resumo?mes=YYYY-MM retorna estrutura correta com totais e quebra por categoria."""
        # Criar categorias
        cat_transporte = client.post("/categorias", json={"nome": "transporte"}).json()["id"]
        cat_alimentacao = client.post("/categorias", json={"nome": "alimentacao"}).json()["id"]

        # Transações de outubro 2026
        client.post("/transacoes", json={"data": "2026-10-01", "descricao": "Salário", "valor": "5000", "tipo": "entrada"})
        client.post("/transacoes", json={"data": "2026-10-05", "descricao": "Uber", "valor": "50", "tipo": "saida", "categoria_id": cat_transporte})
        client.post("/transacoes", json={"data": "2026-10-10", "descricao": "Ônibus", "valor": "10", "tipo": "saida", "categoria_id": cat_transporte})
        client.post("/transacoes", json={"data": "2026-10-15", "descricao": "Restaurante", "valor": "100", "tipo": "saida", "categoria_id": cat_alimentacao})
        client.post("/transacoes", json={"data": "2026-10-20", "descricao": "Sem categoria", "valor": "30", "tipo": "saida"})

        response = client.get("/resumo?mes=2026-10")
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == "2026-10"
        assert data["entradas"] == "5000.00"
        assert data["saidas"] == "190.00"
        assert data["saldo"] == "4810.00"
        assert len(data["por_categoria"]) == 3
        # Verificar categorias (ordenado por total DESC)
        categorias = {item["categoria"]: item["total"] for item in data["por_categoria"]}
        assert categorias["alimentacao"] == "100.00"
        assert categorias["transporte"] == "60.00"
        assert categorias["Sem categoria"] == "30.00"

    def test_resumo_mes_sem_transacoes(self, client: TestClient, db_conn):
        """Mês sem transações retorna zeros e lista vazia."""
        response = client.get("/resumo?mes=2026-08")
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == "2026-08"
        assert data["entradas"] == "0.00"
        assert data["saidas"] == "0.00"
        assert data["saldo"] == "0.00"
        assert data["por_categoria"] == []

    def test_resumo_mes_malformado(self, client: TestClient):
        """Parâmetro mes malformado retorna 422."""
        response = client.get("/resumo?mes=invalido")
        assert response.status_code == 422
        assert "formato YYYY-MM" in response.json()["detail"]

    def test_resumo_mes_invalido_13(self, client: TestClient):
        """Mês inválido (13) retorna 422."""
        response = client.get("/resumo?mes=2026-13")
        assert response.status_code == 422
        assert "Mês inválido" in response.json()["detail"]

    def test_resumo_apenas_saidas_na_quebra_categoria(self, client: TestClient, db_conn):
        """Quebra por categoria no resumo inclui apenas saídas (tipo=saida)."""
        cat = client.post("/categorias", json={"nome": "investimento"}).json()["id"]
        # Entrada com categoria - não deve aparecer na quebra por categoria
        client.post("/transacoes", json={"data": "2026-10-01", "descricao": "Dividendos", "valor": "1000", "tipo": "entrada", "categoria_id": cat})
        # Saída com categoria - deve aparecer
        client.post("/transacoes", json={"data": "2026-10-05", "descricao": "Taxa corretora", "valor": "50", "tipo": "saida", "categoria_id": cat})

        response = client.get("/resumo?mes=2026-10")
        assert response.status_code == 200
        data = response.json()
        assert data["entradas"] == "1000.00"
        assert data["saidas"] == "50.00"
        assert len(data["por_categoria"]) == 1
        assert data["por_categoria"][0]["categoria"] == "investimento"
        assert data["por_categoria"][0]["total"] == "50.00"