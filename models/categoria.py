"""Models Pydantic para categorias."""
from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    """Campos comuns de uma categoria."""
    nome: str = Field(min_length=1, max_length=100)


class CategoriaCreate(CategoriaBase):
    """Schema para criar uma categoria (request body)."""
    pass


class CategoriaResponse(CategoriaBase):
    """Schema para resposta com categoria criada/listada."""
    id: int

    model_config = {"from_attributes": True}