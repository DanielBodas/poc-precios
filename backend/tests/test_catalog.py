def test_crud_categorias(client):
    # Create
    response = client.post("/catalog/categorias", json={"nombre": "Lácteos"})
    assert response.status_code == 200
    cat_id = response.json()["id"]

    # List
    response = client.get("/catalog/categorias")
    assert any(c["nombre"] == "Lácteos" for c in response.json())

    # Delete
    response = client.delete(f"/catalog/categorias/{cat_id}")
    assert response.status_code == 200

    # Verify deleted
    response = client.get("/catalog/categorias")
    assert not any(c["id"] == cat_id for c in response.json())

def test_crud_productos(client):
    # Create a category and brand first
    cat = client.post("/catalog/categorias", json={"nombre": "Bebidas"}).json()
    marca = client.post("/catalog/marcas", json={"nombre": "Coca-Cola"}).json()

    # Create product with associations
    prod_data = {
        "nombre": "Refresco Cola 2L",
        "categoria_ids": [cat["id"]],
        "marca_ids": [marca["id"]],
        "unidad_ids": []
    }
    response = client.post("/catalog/productos", json=prod_data)
    assert response.status_code == 200
    prod = response.json()
    assert prod["nombre"] == "Refresco Cola 2L"

    # List products
    response = client.get("/catalog/productos")
    assert any(p["id"] == prod["id"] for p in response.json())

    # Delete product
    response = client.delete(f"/catalog/productos/{prod['id']}")
    assert response.status_code == 200

def test_link_unlink_categoria(client):
    # Setup
    cat = client.post("/catalog/categorias", json={"nombre": "Fruta"}).json()
    prod = client.post("/catalog/productos", json={"nombre": "Manzana", "categoria_ids": []}).json()

    # Link
    response = client.post(f"/catalog/productos/{prod['id']}/categorias/{cat['id']}")
    assert response.status_code == 200

    # Unlink
    response = client.delete(f"/catalog/productos/{prod['id']}/categorias/{cat['id']}")
    assert response.status_code == 200
