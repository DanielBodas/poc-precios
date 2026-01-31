import pytest
from backend import models
from backend.main import create_access_token

@pytest.fixture
def auth_client(client, db):
    user = models.User(email="test@example.com", name="Test User", role="user")
    db.add(user)
    db.commit()
    token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    client.cookies.set("access_token", token)
    return client

def test_create_and_list_prices(auth_client, db):
    # Setup necessary catalog items
    cat = models.Categoria(nombre="Test Cat")
    marca = models.Marca(nombre="Test Marca")
    sup = models.Supermercado(nombre="Test Sup")
    unit = models.Unidad(nombre="kg")
    prod = models.Producto(nombre="Test Prod")
    db.add_all([cat, marca, sup, unit, prod])
    db.commit()

    # Create price
    price_data = {
        "producto_id": prod.id,
        "marca_id": marca.id,
        "supermercado_id": sup.id,
        "cantidad": 1.0,
        "unidad": "kg",
        "precio_total": 2.5,
        "es_oferta": False
    }
    response = auth_client.post("/precios", json=price_data)
    assert response.status_code == 201

    # List prices
    response = auth_client.get("/precios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["producto"] == "Test Prod"
    assert data[0]["precio_total"] == 2.5
