from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    productos = relationship("Producto", back_populates="categoria")

class Marca(Base):
    __tablename__ = "marcas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    
    precios = relationship("Precio", back_populates="marca_rel")

class Supermercado(Base):
    __tablename__ = "supermercados"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    precios = relationship("Precio", back_populates="supermercado_rel")

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    
    categoria = relationship("Categoria", back_populates="productos")
    precios = relationship("Precio", back_populates="producto_rel")

class Precio(Base):
    __tablename__ = "precios"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    supermercado_id = Column(Integer, ForeignKey("supermercados.id"))
    
    # Datos de la compra
    cantidad = Column(Float)
    unidad = Column(String)
    precio_total = Column(Float)
    precio_unidad = Column(Float)
    
    es_oferta = Column(Boolean, default=False)
    tipo_oferta = Column(String, nullable=True)
    fecha = Column(String)

    producto_rel = relationship("Producto", back_populates="precios")
    marca_rel = relationship("Marca", back_populates="precios")
    supermercado_rel = relationship("Supermercado", back_populates="precios")
