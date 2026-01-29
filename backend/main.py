from typing import List
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt

import os
import json
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# OAuth Imports
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from . import models, schemas
from .database import engine, SessionLocal

# Re-crear tablas (Nota: SQLAlchemy no migra automáticamente cambios en tablas existentes)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceTracker Pro API")

# --- Security & Session Config ---
# Leemos SECRET_KEY de env o usamos uno por defecto para dev
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super_secret_dev_key"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- OAuth Config ---
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- JWT Configuration ---
SECRET_KEY = os.getenv("SESSION_SECRET", "super_secret_dev_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_email(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.PyJWTError:
        return None


# --- Dependency ---
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- Auth Routes ---
@app.get('/login/google')
async def login_google(request: Request):
    # Construct Redirect URI dynamically based on configured API_URL, BACKEND_URL or Host
    base_url = os.getenv('API_URL') or os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
    if base_url.endswith('/'): base_url = base_url[:-1]
    redirect_uri = f"{base_url}/auth/google/callback"
    
    print(f"DEBUG: Initiating Google Login with redirect_uri={redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/google/callback')
async def auth_google(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
             # Fallback if userinfo not in token
             print("DEBUG: Fetching userinfo manually")
             user_info = await oauth.google.userinfo(token=token)
        
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        print(f"DEBUG: Authenticated user: {email}")
        
        # Check if user exists
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            # Create new user
            user = models.User(email=email, name=name, picture=picture, role="user")
            db.add(user)
            db.commit()
            db.refresh(user)
            print("DEBUG: Created new user in DB")
        else:
            # Update info if needed
            if user.name != name or user.picture != picture:
                user.name = name
                user.picture = picture
                db.commit()
        
        # Create JWT Token
        access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
        
        # Redirect to Frontend Home with Token
        base_url = os.getenv('API_URL') or os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
        # Assuming frontend is served statically or on a known port. 
        # If frontend is separate (e.g. port 5500), we should redirect there.
        # Ideally, use an allowed frontend origin from env.
        frontend_url = "http://127.0.0.1:5500/frontend/home.html" # Default to typical local setup
        # Or better: relative path if served by same origin
        return RedirectResponse(url=f'/home.html?token={access_token}')
        
    except Exception as e:
        print(f"Auth Error: {e}")
        return Response(f"Authentication Failed: {str(e)}", status_code=400)

@app.get("/users/me")
def read_users_me(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    email = get_current_user_email(token)
    if not email:
         raise HTTPException(status_code=401, detail="Invalid token")
         
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "role": user.role
    }


# --- Endpoints de Configuración ---
@app.get("/config.js")
def get_config():
    backend_url = os.getenv("API_URL") or os.getenv("BACKEND_URL") or ""
    print(f"DEBUG: Serving config.js with BACKEND_URL='{backend_url}'")
    content = f"window.BACKEND_URL = '{backend_url}';"
    return Response(content=content, media_type="application/javascript")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Catálogo: Categorías ---
@app.get("/catalog/categorias", response_model=List[schemas.Categoria])
def get_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).order_by(models.Categoria.nombre).all()

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
    return db.query(models.Marca).order_by(models.Marca.nombre).all()

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

# --- Catálogo: Unidades ---
@app.get("/catalog/unidades", response_model=List[schemas.Unidad])
def get_unidades(db: Session = Depends(get_db)):
    return db.query(models.Unidad).order_by(models.Unidad.nombre).all()

@app.post("/catalog/unidades", response_model=schemas.Unidad)
def create_unidad(uni: schemas.UnidadCreate, db: Session = Depends(get_db)):
    nueva = models.Unidad(nombre=uni.nombre)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.delete("/catalog/unidades/{id}")
def delete_unidad(id: int, db: Session = Depends(get_db)):
    db.query(models.Unidad).filter(models.Unidad.id == id).delete()
    db.commit()
    return {"status": "ok"}

# --- Catálogo: Supermercados ---
@app.get("/catalog/supermercados", response_model=List[schemas.Supermercado])
def get_supermercados(db: Session = Depends(get_db)):
    return db.query(models.Supermercado).order_by(models.Supermercado.nombre).all()

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
    print(f"DEBUG: Creating product with name='{prod.nombre}', categoria_ids={prod.categoria_ids}, unidad_ids={prod.unidad_ids}, marca_ids={prod.marca_ids}")
    
    if not prod.nombre or not prod.nombre.strip():
        raise HTTPException(400, "El nombre del producto es obligatorio")
    
    nuevo = models.Producto(nombre=prod.nombre.strip())
    
    # Vinculamos Categorías
    if prod.categoria_ids:
        cats = db.query(models.Categoria).filter(models.Categoria.id.in_(prod.categoria_ids)).all()
        nuevo.categorias = cats
        print(f"DEBUG: Linked {len(cats)} categories")
    
    # Vinculamos Unidades
    if prod.unidad_ids:
        unis = db.query(models.Unidad).filter(models.Unidad.id.in_(prod.unidad_ids)).all()
        nuevo.unidades = unis
        print(f"DEBUG: Linked {len(unis)} units")
    
    # Vinculamos Marcas
    if prod.marca_ids:
        marcas = db.query(models.Marca).filter(models.Marca.id.in_(prod.marca_ids)).all()
        nuevo.marcas = marcas
        print(f"DEBUG: Linked {len(marcas)} brands")

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    print(f"DEBUG: Product created successfully with id={nuevo.id}")
    return nuevo

@app.delete("/catalog/productos/{id}")
def delete_producto(id: int, db: Session = Depends(get_db)):
    db.query(models.Producto).filter(models.Producto.id == id).delete()
    db.commit()
    return {"status": "ok"}

# --- Relaciones Producto-Categoria ---
@app.post("/catalog/productos/{producto_id}/categorias/{categoria_id}")
def link_producto_categoria(producto_id: int, categoria_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    cat = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not prod or not cat: raise HTTPException(404, "No existe producto o categoría")
    if cat not in prod.categorias:
        prod.categorias.append(cat)
        db.commit()
    return {"status": "ok"}

@app.delete("/catalog/productos/{producto_id}/categorias/{categoria_id}")
def unlink_producto_categoria(producto_id: int, categoria_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    cat = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if prod and cat and cat in prod.categorias:
        prod.categorias.remove(cat)
        db.commit()
    return {"status": "ok"}

# --- Relaciones Producto-Unidad ---
@app.post("/catalog/productos/{producto_id}/unidades/{unidad_id}")
def link_producto_unidad(producto_id: int, unidad_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    unit = db.query(models.Unidad).filter(models.Unidad.id == unidad_id).first()
    if not prod or not unit: raise HTTPException(404, "No existe producto o unidad")
    if unit not in prod.unidades:
        prod.unidades.append(unit)
        db.commit()
    return {"status": "ok"}

@app.delete("/catalog/productos/{producto_id}/unidades/{unidad_id}")
def unlink_producto_unidad(producto_id: int, unidad_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    unit = db.query(models.Unidad).filter(models.Unidad.id == unidad_id).first()
    if prod and unit and unit in prod.unidades:
        prod.unidades.remove(unit)
        db.commit()
    return {"status": "ok"}

# --- Relaciones Producto-Marca ---
@app.post("/catalog/productos/{producto_id}/marcas/{marca_id}")
def link_producto_marca(producto_id: int, marca_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    marca = db.query(models.Marca).filter(models.Marca.id == marca_id).first()
    if not prod or not marca: raise HTTPException(404, "No existe producto o marca")
    if marca not in prod.marcas:
        prod.marcas.append(marca)
        db.commit()
    return {"status": "ok"}

@app.delete("/catalog/productos/{producto_id}/marcas/{marca_id}")
def unlink_producto_marca(producto_id: int, marca_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    marca = db.query(models.Marca).filter(models.Marca.id == marca_id).first()
    if prod and marca and marca in prod.marcas:
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
        # Skip if product was deleted
        if not p.producto_rel or not p.marca_rel or not p.supermercado_rel:
            continue
            
        cats_str = ", ".join([c.nombre for c in p.producto_rel.categorias]) if p.producto_rel.categorias else "Sin categoría"
        res.append({
            "id": p.id,
            "producto_id": p.producto_id,
            "marca_id": p.marca_id,
            "supermercado_id": p.supermercado_id,
            "producto": p.producto_rel.nombre,
            "marca": p.marca_rel.nombre,
            "categoria": cats_str,
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
    if not p.producto_rel or not p.marca_rel or not p.supermercado_rel:
        raise HTTPException(404, "Producto, marca o supermercado relacionado fue eliminado")
        
    cats_str = ", ".join([c.nombre for c in p.producto_rel.categorias]) if p.producto_rel.categorias else "Sin categoría"
    return {
        "id": p.id,
        "producto_id": p.producto_id,
        "marca_id": p.marca_id,
        "supermercado_id": p.supermercado_id,
        "producto": p.producto_rel.nombre,
        "marca": p.marca_rel.nombre,
        "categoria": cats_str,
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
        # Skip if related objects were deleted
        if not p.producto_rel or not p.marca_rel or not p.supermercado_rel:
            continue
            
        cats_str = ", ".join([c.nombre for c in p.producto_rel.categorias]) if p.producto_rel.categorias else "Sin categoría"
        res.append({
            "id": p.id,
            "producto_id": p.producto_id,
            "marca_id": p.marca_id,
            "supermercado_id": p.supermercado_id,
            "producto": p.producto_rel.nombre,
            "marca": p.marca_rel.nombre,
            "categoria": cats_str,
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

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        # Semilla de Unidades
        if not db.query(models.Unidad).first():
            units = ["kg", "g", "L", "ml", "ud", "pack"]
            for u in units:
                db.add(models.Unidad(nombre=u))
            db.commit()

        # Semilla de Categorías
        if not db.query(models.Categoria).first():
            cats = ["Bebidas", "Lácteos", "Despensa", "Carnicería", "Frutería", "Limpieza", "Higiene", "Ofertas", "Bio"]
            for c in cats:
                db.add(models.Categoria(nombre=c))
            db.commit()

        # Semilla de Supermercados
        if not db.query(models.Supermercado).first():
            supers = ["Mercadona", "Carrefour", "Lidl", "Aldi", "Dia", "Eroski", "Alcampo", "Hipercor"]
            for s in supers:
                db.add(models.Supermercado(nombre=s))
            db.commit()

        # Semilla de Marcas
        if not db.query(models.Marca).first():
            marcas = ["Hacendado", "Carrefour", "Nestlé", "Coca-Cola", "Danone", "Pascual", "Fairy", "Ariel"]
            for m in marcas:
                db.add(models.Marca(nombre=m))
            db.commit()
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        db.close()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
