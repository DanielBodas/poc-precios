from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from .database import Base

# Tabla de relación muchos-a-muchos entre Productos y Marcas
producto_marca = Table(
    "producto_marca",
    Base.metadata,
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True),
    Column("marca_id", Integer, ForeignKey("marcas.id"), primary_key=True),
)

# Tabla de relación muchos-a-muchos entre Productos y Categorías
producto_categoria = Table(
    "producto_categoria",
    Base.metadata,
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True),
    Column("categoria_id", Integer, ForeignKey("categorias.id"), primary_key=True),
)

# Tabla de relación muchos-a-muchos entre Productos y Unidades
producto_unidad = Table(
    "producto_unidad",
    Base.metadata,
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True),
    Column("unidad_id", Integer, ForeignKey("unidades.id"), primary_key=True),
)

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    productos = relationship("Producto", secondary=producto_categoria, back_populates="categorias")

class Marca(Base):
    __tablename__ = "marcas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    
    precios = relationship("Precio", back_populates="marca_rel")
    productos = relationship("Producto", secondary=producto_marca, back_populates="marcas")

class Supermercado(Base):
    __tablename__ = "supermercados"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    precios = relationship("Precio", back_populates="supermercado_rel")

class Unidad(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True) # kg, g, L, ml, ud, etc.
    productos = relationship("Producto", secondary=producto_unidad, back_populates="unidades")

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    
    categorias = relationship("Categoria", secondary=producto_categoria, back_populates="productos")
    unidades = relationship("Unidad", secondary=producto_unidad, back_populates="productos")
    marcas = relationship("Marca", secondary=producto_marca, back_populates="productos")
    precios = relationship("Precio", back_populates="producto_rel")

class Precio(Base):
    __tablename__ = "precios"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    supermercado_id = Column(Integer, ForeignKey("supermercados.id"))
    
    cantidad = Column(Float)
    unidad = Column(String) # Mantenemos el string por ahora para evitar romper histórico de precios si no queremos migrar todo, o podríamos usar FK a Unidad. Dada la petición, parece que Unidad es más una restricción para Producto.
    precio_total = Column(Float)
    precio_unidad = Column(Float)
    
    es_oferta = Column(Boolean, default=False)
    tipo_oferta = Column(String, nullable=True)
    fecha = Column(String)

    producto_rel = relationship("Producto", back_populates="precios")
    marca_rel = relationship("Marca", back_populates="precios")
    supermercado_rel = relationship("Supermercado", back_populates="precios")
