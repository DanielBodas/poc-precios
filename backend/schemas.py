from pydantic import BaseModel
from typing import List, Optional

# --- Categoria ---
class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    class Config: from_attributes = True

# --- Marca ---
class MarcaBase(BaseModel):
    nombre: str

class MarcaCreate(MarcaBase):
    pass

class Marca(MarcaBase):
    id: int
    class Config: from_attributes = True

# --- Supermercado ---
class SupermercadoBase(BaseModel):
    nombre: str

class SupermercadoCreate(SupermercadoBase):
    pass

class Supermercado(SupermercadoBase):
    id: int
    class Config: from_attributes = True

# --- Producto ---
class ProductoBase(BaseModel):
    nombre: str
    categoria_id: int

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id: int
    categoria: Optional[Categoria] = None
    class Config: from_attributes = True

# --- Precio ---
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
    tipo_oferta: Optional[str] = None
    fecha: str
