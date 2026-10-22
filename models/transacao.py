"""Models Pydantic para transações."""
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


TipoTransacao = Literal["entrada", "saida"]


class TransacaoBase(BaseModel):
    """Campos comuns de uma transação."""
    data: date
    descricao: str = Field(min_length=1, max_length=200)
    valor: Decimal = Field(gt=0, decimal_places=2)
    tipo: TipoTransacao
    categoria_id: Optional[int] = Field(default=None, ge=1)

    @field_validator("valor", mode="before")
    @classmethod
    def validate_valor(cls, v):
        """Garante que o valor tenha no máximo 2 casas decimais."""
        if isinstance(v, float):
            return Decimal(str(v))
        if isinstance(v, (int, str)):
            return Decimal(str(v))
        return v


class TransacaoCreate(TransacaoBase):
    """Schema para criar uma transação (request body)."""
    pass


class TransacaoResponse(TransacaoBase):
    """Schema para resposta com transação criada/listada."""
    id: int

    model_config = {"from_attributes": True}