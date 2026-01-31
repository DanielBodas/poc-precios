def test_crud_precios(client):
    # Setup dependencies
    cat = client.post("/catalog/categorias", json={"nombre": "Despensa"}).json()
    marca = client.post("/catalog/marcas", json={"nombre": "Hacendado"}).json()
    supermercado = client.post("/catalog/supermercados", json={"nombre": "Mercadona"}).json()
    prod = client.post("/catalog/productos", json={
        "nombre": "Arroz",
        "categoria_ids": [cat["id"]],
        "marca_ids": [marca["id"]]
    }).json()

    # Create Price
    precio_data = {
        "producto_id": prod["id"],
        "marca_id": marca["id"],
        "supermercado_id": supermercado["id"],
        "cantidad": 1,
        "unidad": "kg",
        "precio_total": 1.20,
        "es_oferta": False,
        "tipo_oferta": ""
    }
    response = client.post("/precios", json=precio_data)
    assert response.status_code == 201

    # List Prices
    response = client.get("/precios")
    precios = response.json()
    assert len(precios) > 0
    p = precios[0]
    assert p["producto"] == "Arroz"
    assert p["precio_unidad"] == 1.20

    # Historial
    response = client.get(f"/precios/producto/{prod['id']}")
    historial = response.json()
    assert len(historial) == 1
    assert historial[0]["precio_total"] == 1.20

def test_precio_unidad_calculo(client):
    # Setup
    cat = client.post("/catalog/categorias", json={"nombre": "Limpieza"}).json()
    marca = client.post("/catalog/marcas", json={"nombre": "Fairy"}).json()
    super = client.post("/catalog/supermercados", json={"nombre": "Lidl"}).json()
    prod = client.post("/catalog/productos", json={"nombre": "Lavavajillas"}).json()

    # Create Price with quantity 2
    precio_data = {
        "producto_id": prod["id"],
        "marca_id": marca["id"],
        "supermercado_id": super["id"],
        "cantidad": 2,
        "unidad": "ud",
        "precio_total": 5.00,
        "es_oferta": True,
        "tipo_oferta": "2x1"
    }
    client.post("/precios", json=precio_data)

    response = client.get("/precios")
    p = response.json()[0]
    assert p["precio_unidad"] == 2.50
