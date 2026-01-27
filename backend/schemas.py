from pydantic import BaseModel
from typing import List, Optional

# --- Categoria ---
class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase): pass

class Categoria(CategoriaBase):
    id: int
    class Config: from_attributes = True

# --- Marca ---
class MarcaBase(BaseModel):
    nombre: str

class MarcaCreate(MarcaBase): pass

class Marca(MarcaBase):
    id: int
    class Config: from_attributes = True

# --- Unidad ---
class UnidadBase(BaseModel):
    nombre: str

class UnidadCreate(UnidadBase): pass

class Unidad(UnidadBase):
    id: int
    class Config: from_attributes = True

# --- Producto ---
class ProductoBase(BaseModel):
    nombre: str

class ProductoCreate(ProductoBase):
    categoria_ids: List[int] = []
    unidad_ids: List[int] = []
    marca_ids: List[int] = []

class Producto(ProductoBase):
    id: int
    categorias: List[Categoria] = []
    unidades: List[Unidad] = []
    marcas: List[Marca] = []
    class Config: from_attributes = True

# --- Supermercado ---
class SupermercadoBase(BaseModel):
    nombre: str

class SupermercadoCreate(SupermercadoBase): pass

class Supermercado(SupermercadoBase):
    id: int
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

class PrecioUpdate(BaseModel):
    producto_id: Optional[int] = None
    marca_id: Optional[int] = None
    supermercado_id: Optional[int] = None
    cantidad: Optional[float] = None
    unidad: Optional[str] = None
    precio_total: Optional[float] = None
    es_oferta: Optional[bool] = None
    tipo_oferta: Optional[str] = None

class PrecioDisplay(BaseModel):
    id: int
    producto_id: int
    marca_id: int
    supermercado_id: int
    producto: str
    marca: str
    categoria: str # Mostrará categorías separadas por comas
    supermercado: str
    cantidad: float
    unidad: str
    precio_total: float
    precio_unidad: float
    es_oferta: bool
    tipo_oferta: Optional[str] = None
    fecha: str

