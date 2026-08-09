from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Product, StockMovement
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables and seed test data before each test"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    product = Product(
        name="Test Mouse",
        sku="TEST-001",
        description="A test product",
        current_stock=100,
        price=29.99
    )
    db.add(product)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


class TestHealth:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCreateProduct:
    def test_create_product_success(self):
        response = client.post("/api/products", json={
            "name": "Gaming Mouse",
            "sku": "TECH-011",
            "description": "RGB gaming mouse",
            "current_stock": 25,
            "price": 49.99
        })
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == "TECH-011"
        assert data["name"] == "Gaming Mouse"
        assert data["current_stock"] == 25

    def test_create_product_duplicate_sku(self):
        response = client.post("/api/products", json={
            "name": "Another Mouse",
            "sku": "TEST-001",
            "current_stock": 10
        })
        assert response.status_code == 409

    def test_create_product_negative_stock(self):
        response = client.post("/api/products", json={
            "name": "Negative Stock",
            "sku": "TECH-012",
            "current_stock": -5
        })
        assert response.status_code == 422

    def test_create_product_name_too_long(self):
        response = client.post("/api/products", json={
            "name": "A" * 256,
            "sku": "TECH-013",
            "current_stock": 10
        })
        assert response.status_code == 422

    def test_create_product_with_zero_stock(self):
        response = client.post("/api/products", json={
            "name": "Zero Stock",
            "sku": "TECH-014",
            "current_stock": 0
        })
        assert response.status_code == 201
        data = response.json()
        assert data["current_stock"] == 0


class TestAddStock:
    def test_add_stock_success(self):
        response = client.post("/api/inventory/add-stock", json={
            "sku": "TEST-001",
            "quantity": 50
        })
        assert response.status_code == 200
        data = response.json()
        assert data["movement_type"] == "add"
        assert data["quantity"] == 50
        assert data["previous_stock"] == 100
        assert data["new_stock"] == 150

    def test_add_stock_product_not_found(self):
        response = client.post("/api/inventory/add-stock", json={
            "sku": "NONEXISTENT",
            "quantity": 10
        })
        assert response.status_code == 404

    def test_add_stock_invalid_quantity(self):
        response = client.post("/api/inventory/add-stock", json={
            "sku": "TEST-001",
            "quantity": -5
        })
        assert response.status_code == 422

    def test_add_stock_zero_quantity(self):
        response = client.post("/api/inventory/add-stock", json={
            "sku": "TEST-001",
            "quantity": 0
        })
        assert response.status_code == 422

    def test_add_stock_reference_too_long(self):
        response = client.post("/api/inventory/add-stock", json={
            "sku": "TEST-001",
            "quantity": 10,
            "reference": "A" * 256
        })
        assert response.status_code == 422

    def test_add_stock_notes_too_long(self):
        response = client.post("/api/inventory/add-stock", json={
            "sku": "TEST-001",
            "quantity": 10,
            "notes": "B" * 501
        })
        assert response.status_code == 422


class TestRemoveStock:
    def test_remove_stock_success(self):
        response = client.post("/api/inventory/remove-stock", json={
            "sku": "TEST-001",
            "quantity": 30
        })
        assert response.status_code == 200
        data = response.json()
        assert data["movement_type"] == "remove"
        assert data["previous_stock"] == 100
        assert data["new_stock"] == 70

    def test_remove_stock_insufficient(self):
        response = client.post("/api/inventory/remove-stock", json={
            "sku": "TEST-001",
            "quantity": 999
        })
        assert response.status_code == 400

    def test_remove_stock_product_not_found(self):
        response = client.post("/api/inventory/remove-stock", json={
            "sku": "NONEXISTENT",
            "quantity": 10
        })
        assert response.status_code == 404

    def test_remove_stock_quantity_too_high(self):
        response = client.post("/api/inventory/remove-stock", json={
            "sku": "TEST-001",
            "quantity": 9999999
        })
        assert response.status_code == 400


class TestGetStock:
    def test_get_all_stock(self):
        response = client.get("/api/inventory/stock")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sku"] == "TEST-001"

    def test_get_stock_default_pagination(self):
        response = client.get("/api/inventory/stock")
        assert response.status_code == 200

    def test_get_stock_custom_pagination(self):
        response = client.get("/api/inventory/stock?offset=0&limit=10")
        assert response.status_code == 200

    def test_get_stock_negative_offset(self):
        response = client.get("/api/inventory/stock?offset=-5")
        assert response.status_code == 422

    def test_get_stock_negative_limit(self):
        response = client.get("/api/inventory/stock?limit=-10")
        assert response.status_code == 422

    def test_get_stock_limit_too_high(self):
        response = client.get("/api/inventory/stock?limit=101")
        assert response.status_code == 422


class TestGetProduct:
    def test_get_product_success(self):
        response = client.get("/api/products/TEST-001")
        assert response.status_code == 200
        data = response.json()
        assert data["sku"] == "TEST-001"
        assert data["name"] == "Test Mouse"
        assert data["current_stock"] == 100

    def test_get_product_not_found(self):
        response = client.get("/api/products/NONEXISTENT")
        assert response.status_code == 404


class TestMovements:
    def test_get_movements_empty(self):
        response = client.get("/api/inventory/movements/TEST-001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_movements_with_history(self):
        client.post("/api/inventory/add-stock", json={
            "sku": "TEST-001",
            "quantity": 50
        })
        client.post("/api/inventory/remove-stock", json={
            "sku": "TEST-001",
            "quantity": 20
        })
        response = client.get("/api/inventory/movements/TEST-001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["movement_type"] == "remove"
        assert data[1]["movement_type"] == "add"

    def test_get_movements_product_not_found(self):
        response = client.get("/api/inventory/movements/NONEXISTENT")
        assert response.status_code == 404

    def test_get_movements_pagination(self):
        response = client.get("/api/inventory/movements/TEST-001?offset=0&limit=5")
        assert response.status_code == 200

    def test_get_movements_negative_skip(self):
        response = client.get("/api/inventory/movements/TEST-001?offset=-1")
        assert response.status_code == 422


class TestErrorHandling:
    def test_500_does_not_leak_internals(self):
        response = client.get("/api/inventory/stock?offset=-5&limit=-10")
        assert response.status_code == 422
        data = response.json()
        assert "SQL" not in str(data)
        assert "psycopg2" not in str(data)
        assert "sqlalchemy" not in str(data)

    def test_500_does_not_leak_db_error(self):
        response = client.post("/api/inventory/add-stock", json={
            "sku": "TEST-001",
            "quantity": 10,
            "reference": "A" * 256
        })
        assert response.status_code == 422
        data = response.json()
        assert "value too long" not in str(data).lower()
        assert "character varying" not in str(data).lower()


class TestFullWorkflow:
    def test_create_add_remove_workflow(self):
        # Create product
        r1 = client.post("/api/products", json={
            "name": "Workflow Test",
            "sku": "FLOW-001",
            "current_stock": 50
        })
        assert r1.status_code == 201

        # Add stock
        r2 = client.post("/api/inventory/add-stock", json={
            "sku": "FLOW-001",
            "quantity": 25
        })
        assert r2.status_code == 200
        assert r2.json()["new_stock"] == 75

        # Remove stock
        r3 = client.post("/api/inventory/remove-stock", json={
            "sku": "FLOW-001",
            "quantity": 15
        })
        assert r3.status_code == 200
        assert r3.json()["new_stock"] == 60

        # Verify final state
        r4 = client.get("/api/products/FLOW-001")
        assert r4.status_code == 200
        assert r4.json()["current_stock"] == 60

        # Check movements
        r5 = client.get("/api/inventory/movements/FLOW-001")
        assert r5.status_code == 200
        assert len(r5.json()) == 3  # initial + add + remove
