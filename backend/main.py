from typing import List
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
from fastapi.staticfiles import StaticFiles

from . import models, schemas
from .database import engine, SessionLocal

# Re-crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceTracker Pro API")

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- Endpoints de Configuración ---
@app.get("/config.js")
def get_config():
    backend_url = os.getenv("BACKEND_URL", "")
    content = f"window.BACKEND_URL = '{backend_url}';"
    return Response(content=content, media_type="application/javascript")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# --- Relaciones Producto-Marca ---
@app.post("/catalog/relacionar-producto-marca")
def link_prod_marca(data: schemas.LinkProductoMarca, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == data.producto_id).first()
    marca = db.query(models.Marca).filter(models.Marca.id == data.marca_id).first()
    if not prod or not marca: raise HTTPException(404, "No existe producto o marca")
    if marca not in prod.marcas:
        prod.marcas.append(marca)
        db.commit()
    return {"status": "ok"}

@app.delete("/catalog/desvincular-producto-marca")
def unlink_prod_marca(producto_id: int, marca_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    marca = db.query(models.Marca).filter(models.Marca.id == marca_id).first()
    if marca in prod.marcas:
        prod.marcas.remove(marca)
        db.commit()
    return {"status": "ok"}

# --- Registros de Precios ---
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
    res = []
    for p in precios:
        res.append({
            "id": p.id,
            "producto_id": p.producto_id,
            "marca_id": p.marca_id,
            "supermercado_id": p.supermercado_id,
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
    return res

@app.get("/precios/{id}", response_model=schemas.PrecioDisplay)
def get_precio(id: int, db: Session = Depends(get_db)):
    p = db.query(models.Precio).filter(models.Precio.id == id).first()
    if not p: raise HTTPException(404, "No existe")
    return {
        "id": p.id,
        "producto_id": p.producto_id,
        "marca_id": p.marca_id,
        "supermercado_id": p.supermercado_id,
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
    }

@app.put("/precios/{id}")
def update_precio(id: int, data: schemas.PrecioUpdate, db: Session = Depends(get_db)):
    p = db.query(models.Precio).filter(models.Precio.id == id).first()
    if not p: raise HTTPException(404, "No existe")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(p, field, value)
    
    # Recalcular precio unidad
    p.precio_unidad = p.precio_total / p.cantidad if p.cantidad > 0 else 0
    db.commit()
    return {"status": "ok"}

@app.delete("/precios/{id}")
def delete_precio(id: int, db: Session = Depends(get_db)):
    db.query(models.Precio).filter(models.Precio.id == id).delete()
    db.commit()
    return {"status": "ok"}

@app.get("/precios/producto/{prod_id}", response_model=List[schemas.PrecioDisplay])
def historial_producto(prod_id: int, db: Session = Depends(get_db)):
    precios = db.query(models.Precio).filter(models.Precio.producto_id == prod_id).order_by(models.Precio.id.desc()).all()
    res = []
    for p in precios:
        res.append({
            "id": p.id,
            "producto_id": p.producto_id,
            "marca_id": p.marca_id,
            "supermercado_id": p.supermercado_id,
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
    return res

# Startup seeding logic (mantener similar)
@app.on_event("startup")
def startup_db_fix():
    # Pequeño script de migración para SQLite (PoC)
    # SQLAlchemy create_all no añade columnas a tablas existentes
    db = SessionLocal()
    try:
        from sqlalchemy import text
        # Intentar añadir la columna unidades_permitidas si no existe
        if engine.url.drivername == "sqlite":
            try:
                db.execute(text("ALTER TABLE productos ADD COLUMN unidades_permitidas TEXT"))
                db.commit()
            except:
                db.rollback()
    finally:
        db.close()

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if not db.query(models.Categoria).first():
        # ... logic inherited from before for initial seed ...
        pass
    db.close()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
