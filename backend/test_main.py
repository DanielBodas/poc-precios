import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from backend.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_catalog_categorias():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/catalog/categorias")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Should have seeded data
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_security_headers():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers
