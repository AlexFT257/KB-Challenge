import pytest
from fastapi.testclient import TestClient

# Just import after setting the env var
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Product

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables and seed test data"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        product = Product(
            name="Test Mouse",
            sku="TEST-001",
            description="A test product",
            current_stock=100,
            price=29.99
        )
        db.add(product)
        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)
