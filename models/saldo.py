"""Models Pydantic para saldo e resumo mensal."""
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List


class SaldoResponse(BaseModel):
    """Schema para resposta do saldo total."""
    entradas: Decimal = Field(ge=0, decimal_places=2)
    saidas: Decimal = Field(ge=0, decimal_places=2)
    saldo: Decimal = Field(decimal_places=2)

    model_config = {"from_attributes": True}


class ResumoCategoria(BaseModel):
    """Schema para cada categoria no resumo mensal."""
    categoria: str
    total: Decimal = Field(ge=0, decimal_places=2)

    model_config = {"from_attributes": True}


class ResumoResponse(BaseModel):
    """Schema para resposta do resumo mensal."""
    mes: str
    entradas: Decimal = Field(ge=0, decimal_places=2)
    saidas: Decimal = Field(ge=0, decimal_places=2)
    saldo: Decimal = Field(decimal_places=2)
    por_categoria: List[ResumoCategoria]

    model_config = {"from_attributes": True}