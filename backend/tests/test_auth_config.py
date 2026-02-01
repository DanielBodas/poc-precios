import os
import jwt
from backend.main import SECRET_KEY, ALGORITHM

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_config_js_default(client):
    # Clear env vars if they exist
    if "API_URL" in os.environ: del os.environ["API_URL"]
    if "BACKEND_URL" in os.environ: del os.environ["BACKEND_URL"]

    response = client.get("/config.js")
    assert response.status_code == 200
    assert "window.BACKEND_URL = '';" in response.text
    assert "no-cache" in response.headers["Cache-Control"]

def test_config_js_with_env(client):
    os.environ["API_URL"] = "https://api.myapp.com/"
    response = client.get("/config.js")
    assert response.status_code == 200
    # Should strip trailing slash
    assert "window.BACKEND_URL = 'https://api.myapp.com';" in response.text
    del os.environ["API_URL"]

def test_login_google_redirect(client):
    os.environ["BACKEND_URL"] = "http://production.com"
    # We follow_redirects=False to check the Location header
    response = client.get("/login/google", follow_redirects=False)
    assert response.status_code == 302
    location = response.headers["Location"]
    assert "accounts.google.com" in location
    assert "redirect_uri=http%3A%2F%2Fproduction.com%2Fauth%2Fgoogle%2Fcallback" in location
    del os.environ["BACKEND_URL"]

def test_read_users_me_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_read_users_me_success(client, db_session):
    from backend import models
    # Create a user in DB
    user = models.User(email="test@example.com", name="Test User", role="user")
    db_session.add(user)
    db_session.commit()

    # Generate token
    token_data = {"sub": "test@example.com"}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
