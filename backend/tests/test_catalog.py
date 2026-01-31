import pytest
from backend import models
from backend.main import create_access_token

@pytest.fixture
def admin_client(client, db):
    user = models.User(email="admin@example.com", name="Admin User", role="admin")
    db.add(user)
    db.commit()
    token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    client.cookies.set("access_token", token)
    return client

def test_catalog_management(admin_client, db):
    # Create category
    res = admin_client.post("/catalog/categorias", json={"nombre": "Dairy"})
    assert res.status_code == 200
    cat_id = res.json()["id"]

    # Create brand
    res = admin_client.post("/catalog/marcas", json={"nombre": "Nestle"})
    assert res.status_code == 200
    marca_id = res.json()["id"]

    # Create product with linked entities
    prod_data = {
        "nombre": "Milk",
        "categoria_ids": [cat_id],
        "marca_ids": [marca_id],
        "unidad_ids": []
    }
    res = admin_client.post("/catalog/productos", json=prod_data)
    assert res.status_code == 200
    prod_id = res.json()["id"]

    # Verify links
    prod = db.query(models.Producto).get(prod_id)
    assert len(prod.categorias) == 1
    assert prod.categorias[0].nombre == "Dairy"
    assert len(prod.marcas) == 1
    assert prod.marcas[0].nombre == "Nestle"

    # Delete category
    res = admin_client.delete(f"/catalog/categorias/{cat_id}")
    assert res.status_code == 200

    # Verify category is gone
    assert db.query(models.Categoria).get(cat_id) is None
