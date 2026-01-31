import pytest
from backend import models
from backend.main import create_access_token

def test_read_landing(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "PriceTracker Pro" in response.text

def test_read_login(client):
    response = client.get("/index.html")
    assert response.status_code == 200
    assert "Iniciar Sesión" in response.text

def test_home_redirect_unauthorized(client):
    # Should redirect to index.html (307 is default for RedirectResponse in some cases, or handled by exception handler)
    # My exception handler returns RedirectResponse(url='/index.html')
    response = client.get("/home.html", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/index.html"

def test_api_unauthorized(client):
    response = client.get("/precios")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_home_authorized(client, db):
    # Create a user
    user = models.User(email="test@example.com", name="Test User", role="user")
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    client.cookies.set("access_token", token)

    response = client.get("/home.html")
    assert response.status_code == 200
    assert "Muro de Precios" in response.text

def test_catalog_access_denied_for_user(client, db):
    user = models.User(email="user@example.com", name="Regular User", role="user")
    db.add(user)
    db.commit()

    token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    client.cookies.set("access_token", token)

    response = client.get("/catalog.html")
    assert response.status_code == 403
    assert "403 Prohibido" in response.text

def test_catalog_access_allowed_for_admin(client, db):
    user = models.User(email="admin@example.com", name="Admin User", role="admin")
    db.add(user)
    db.commit()

    token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    client.cookies.set("access_token", token)

    response = client.get("/catalog.html")
    assert response.status_code == 200
    assert "Gestión de Catálogo" in response.text

def test_admin_api_restricted(client, db):
    # Regular user trying to create a category
    user = models.User(email="user@example.com", name="Regular User", role="user")
    db.add(user)
    db.commit()

    token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    client.cookies.set("access_token", token)

    response = client.post("/catalog/categorias", json={"nombre": "New Cat"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}

def test_admin_api_allowed(client, db):
    # Admin creating a category
    user = models.User(email="admin@example.com", name="Admin User", role="admin")
    db.add(user)
    db.commit()

    token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    client.cookies.set("access_token", token)

    response = client.post("/catalog/categorias", json={"nombre": "New Cat"})
    assert response.status_code == 200
    assert response.json()["nombre"] == "New Cat"

def test_role_assignment_logic(db):
    # Test first user
    email1 = "first@example.com"
    is_first1 = db.query(models.User).count() == 0
    role1 = "admin" if is_first1 else "user"
    user1 = models.User(email=email1, role=role1)
    db.add(user1)
    db.commit()
    assert user1.role == "admin"

    # Test second user
    email2 = "second@example.com"
    is_first2 = db.query(models.User).count() == 0
    role2 = "admin" if is_first2 else "user"
    user2 = models.User(email=email2, role=role2)
    db.add(user2)
    db.commit()
    assert user2.role == "user"
