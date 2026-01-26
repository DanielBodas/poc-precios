from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from . import models, schemas
from .database import engine, SessionLocal

# Re-crear tablas (limpieza para el nuevo modelo profundo)
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceTracker Pro Anti-Scam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if not db.query(models.Categoria).first():
        # Categorías
        cat_lacteos = models.Categoria(nombre="Lácteos")
        cat_aceites = models.Categoria(nombre="Aceites")
        cat_limpieza = models.Categoria(nombre="Limpieza")
        db.add_all([cat_lacteos, cat_aceites, cat_limpieza])
        db.commit()

        # Marcas
        m_hacendado = models.Marca(nombre="Hacendado")
        m_pascual = models.Marca(nombre="Pascual")
        m_carbonell = models.Marca(nombre="Carbonell")
        db.add_all([m_hacendado, m_pascual, m_carbonell])
        db.commit()

        # Productos (Genéricos)
        db.add_all([
            models.Producto(nombre="Leche Entera", categoria_id=cat_lacteos.id),
            models.Producto(nombre="Leche Desnatada", categoria_id=cat_lacteos.id),
            models.Producto(nombre="Aceite de Oliva AOVE 1L", categoria_id=cat_aceites.id)
        ])
        
        # Súpers
        db.add_all([
            models.Supermercado(nombre="Mercadona"),
            models.Supermercado(nombre="Lidl"),
            models.Supermercado(nombre="Carrefour")
        ])
        db.commit()
    db.close()

# --- Catálogo ---

@app.get("/catalog/productos", response_model=List[schemas.Producto])
def get_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).all()

@app.get("/catalog/supermercados", response_model=List[schemas.Supermercado])
def get_supermercados(db: Session = Depends(get_db)):
    return db.query(models.Supermercado).all()

@app.get("/catalog/marcas", response_model=List[schemas.Marca])
def get_marcas(db: Session = Depends(get_db)):
    return db.query(models.Marca).all()

# --- Registro de Precios ---

@app.post("/precios", status_code=201)
def crear_precio(precio: schemas.PrecioCreate, db: Session = Depends(get_db)):
    p_unidad = precio.precio_total / precio.cantidad if precio.cantidad > 0 else 0
    
    nuevo = models.Precio(
        producto_id=precio.producto_id,
        marca_id=precio.marca_id,
        supermercado_id=precio.supermercado_id,
        cantidad=precio.cantidad,
        unidad=precio.unidad,
        precio_total=precio.precio_total,
        precio_unidad=p_unidad,
        es_oferta=precio.es_oferta,
        tipo_oferta=precio.tipo_oferta,
        fecha=datetime.now().isoformat()
    )
    db.add(nuevo)
    db.commit()
    return {"status": "ok"}

@app.get("/precios", response_model=List[schemas.PrecioDisplay])
def listar_precios(db: Session = Depends(get_db)):
    precios = db.query(models.Precio).all()
    resultado = []
    for p in precios:
        resultado.append({
            "id": p.id,
            "producto": p.producto_rel.nombre,
            "marca": p.marca_rel.nombre,
            "categoria": p.producto_rel.categoria.nombre,
            "supermercado": p.supermercado_rel.nombre,
            "cantidad": p.cantidad,
            "unidad": p.unidad,
            "precio_total": p.precio_total,
            "precio_unidad": p.precio_unidad,
            "es_oferta": p.es_oferta,
            "tipo_oferta": p.tipo_oferta,
            "fecha": p.fecha
        })
    return resultado
