from pydantic import BaseModel
from typing import List, Optional

class Categoria(BaseModel):
    id: int
    nombre: str
    class Config: from_attributes = True

class Marca(BaseModel):
    id: int
    nombre: str
    class Config: from_attributes = True

class Supermercado(BaseModel):
    id: int
    nombre: str
    class Config: from_attributes = True

class Producto(BaseModel):
    id: int
    nombre: str
    categoria_id: int
    categoria: Optional[Categoria] = None
    class Config: from_attributes = True

class PrecioCreate(BaseModel):
    producto_id: int
    marca_id: int
    supermercado_id: int
    cantidad: float
    unidad: str
    precio_total: float
    es_oferta: bool = False
    tipo_oferta: Optional[str] = None

class PrecioDisplay(BaseModel):
    id: int
    producto: str
    marca: str
    categoria: str
    supermercado: str
    cantidad: float
    unidad: str
    precio_total: float
    precio_unidad: float
    es_oferta: bool
    tipo_oferta: Optional[str]
    fecha: str
