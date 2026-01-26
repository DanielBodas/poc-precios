from typing import List
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
from fastapi.staticfiles import StaticFiles

from . import models, schemas
from .database import engine, SessionLocal

# Re-crear tablas (Nota: en producción con Postgres podrías querer usar migraciones como Alembic)
# Pero para la PoC lo dejamos así para que funcione al arrancar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceTracker Pro Anti-Scam API")

# --- Endpoints de Configuración ---
@app.get("/config.js")
def get_config():
    # Si no hay variable, dejamos vacío para usar rutas relativas
    backend_url = os.getenv("BACKEND_URL", "")
    content = f"window.BACKEND_URL = '{backend_url}';"
    return Response(content=content, media_type="application/javascript")

# CORS (relevante para desarrollo, en producción serviremos todo desde el mismo origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir el frontend como archivos estáticos
# IMPORTANTE: Esto debe ir DESPUÉS de definir las rutas de la API
# o usar un prefijo para la API

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

# --- Catálogo: Categorías ---

@app.get("/catalog/categorias", response_model=List[schemas.Categoria])
def get_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()

@app.post("/catalog/categorias", response_model=schemas.Categoria)
def create_categoria(cat: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    nueva = models.Categoria(nombre=cat.nombre)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.delete("/catalog/categorias/{id}")
def delete_categoria(id: int, db: Session = Depends(get_db)):
    db.query(models.Categoria).filter(models.Categoria.id == id).delete()
    db.commit()
    return {"status": "ok"}

# --- Catálogo: Marcas ---

@app.get("/catalog/marcas", response_model=List[schemas.Marca])
def get_marcas(db: Session = Depends(get_db)):
    return db.query(models.Marca).all()

@app.post("/catalog/marcas", response_model=schemas.Marca)
def create_marca(marca: schemas.MarcaCreate, db: Session = Depends(get_db)):
    nueva = models.Marca(nombre=marca.nombre)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.delete("/catalog/marcas/{id}")
def delete_marca(id: int, db: Session = Depends(get_db)):
    db.query(models.Marca).filter(models.Marca.id == id).delete()
    db.commit()
    return {"status": "ok"}

# --- Catálogo: Supermercados ---

@app.get("/catalog/supermercados", response_model=List[schemas.Supermercado])
def get_supermercados(db: Session = Depends(get_db)):
    return db.query(models.Supermercado).all()

@app.post("/catalog/supermercados", response_model=schemas.Supermercado)
def create_super(sup: schemas.SupermercadoCreate, db: Session = Depends(get_db)):
    nuevo = models.Supermercado(nombre=sup.nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.delete("/catalog/supermercados/{id}")
def delete_super(id: int, db: Session = Depends(get_db)):
    db.query(models.Supermercado).filter(models.Supermercado.id == id).delete()
    db.commit()
    return {"status": "ok"}

# --- Catálogo: Productos ---

@app.get("/catalog/productos", response_model=List[schemas.Producto])
def get_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).all()

@app.post("/catalog/productos", response_model=schemas.Producto)
def create_producto(prod: schemas.ProductoCreate, db: Session = Depends(get_db)):
    nuevo = models.Producto(nombre=prod.nombre, categoria_id=prod.categoria_id)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.delete("/catalog/productos/{id}")
def delete_producto(id: int, db: Session = Depends(get_db)):
    db.query(models.Producto).filter(models.Producto.id == id).delete()
    db.commit()
    return {"status": "ok"}

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
    precios = db.query(models.Precio).order_by(models.Precio.id.desc()).all()
    resultado = []
    for p in precios:
        resultado.append({
            "id": p.id,
            "producto": p.producto_rel.nombre,
            "marca": p.marca_rel.nombre,
            "categoria": p.producto_rel.categoria.nombre,
            "supermercado": p.supermercado_rel.nombre,
            "cantidad": p.cantidad,
            "unidad": getattr(p, 'unidad', getattr(p, 'unit', 'n/a')),
            "precio_total": p.precio_total,
            "precio_unidad": p.precio_unidad,
            "es_oferta": p.es_oferta,
            "tipo_oferta": p.tipo_oferta,
            "fecha": p.fecha
        })
    return resultado

@app.delete("/precios/{id}")
def delete_precio(id: int, db: Session = Depends(get_db)):
    db.query(models.Precio).filter(models.Precio.id == id).delete()
    db.commit()
    return {"status": "ok"}

# Montar el frontend para archivos estáticos (js, css, etc)
# html=True permite que '/' busque 'index.html' automáticamente
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
