# Inventory Management System

A simple inventory management API built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- Create products with validation
- Add stock (supplier deliveries)
- Remove stock (customer purchases)
- View current stock levels for all products
- Track stock movement history per product
- Full audit trail with before/after stock levels
- Prevents negative inventory
- Input validation at API and database level
- Row-level locking for concurrent operations
- Clean error handling (no internal leaks)

## Tech Stack

- **Python 3.11**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Docker** - Containerization
- **Pytest** - Testing

## Quick Start

```bash
# 1. Clone and enter project
git clone https://github.com/AlexFT257/KB-Challenge
cd KB-Challenge

# 2. Start services
docker-compose up -d

# 3. Seed test data
docker-compose exec web python -m app.seed_data

# 4. Open API docs
open http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/products` | Create a new product |
| `POST` | `/api/inventory/add-stock` | Add stock to a product |
| `POST` | `/api/inventory/remove-stock` | Remove stock from a product |
| `GET` | `/api/inventory/stock` | Get all products stock levels |
| `GET` | `/api/inventory/movements/{sku}` | Track stock movements for a product |
| `GET` | `/api/products/{sku}` | Get product by SKU |
| `GET` | `/health` | Health check |

## Usage Examples

### Create Product
```bash
curl -X POST "http://localhost:8000/api/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse",
    "sku": "TECH-001",
    "description": "Ergonomic wireless mouse",
    "current_stock": 100,
    "price": 29.99
  }'
```

### Add Stock
```bash
curl -X POST "http://localhost:8000/api/inventory/add-stock" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TECH-001",
    "quantity": 50,
    "reference": "PO-2024-001",
    "notes": "Supplier delivery"
  }'
```

### Remove Stock
```bash
curl -X POST "http://localhost:8000/api/inventory/remove-stock" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TECH-001",
    "quantity": 2,
    "reference": "ORDER-12345",
    "notes": "Customer purchase"
  }'
```

### View All Stock
```bash
curl "http://localhost:8000/api/inventory/stock"
```

### Track Product Movements
```bash
curl "http://localhost:8000/api/inventory/movements/TECH-001"
```

### Get Product Details
```bash
curl "http://localhost:8000/api/products/TECH-001"
```

## Project Structure

```
inventory-system/
├── app/
│   ├── main.py          # FastAPI app & endpoints
│   ├── models.py        # SQLAlchemy models (Product, StockMovement)
│   ├── schemas.py       # Pydantic schemas with validation
│   ├── crud.py          # Business logic
│   ├── database.py      # Database connection
│   ├── config.py        # Configuration
│   └── seed_data.py     # Database seeding
├── test_main.py         # Test suite
├── conftest.py          # Test configuration
├── docker-compose.yml   # Docker services (app, db, test-db)
├── Dockerfile           # App container
├── init-db.sql          # Seed data SQL
├── run-tests.sh         # Test runner script
└── requirements.txt     # Python dependencies
```

## Data Models

### Product
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(255) | Required, max 255 chars |
| sku | VARCHAR(100) | Unique, alphanumeric + hyphens/underscores |
| description | VARCHAR(1000) | Optional |
| current_stock | INTEGER | Default 0, non-negative |
| price | NUMERIC(10,2) | Optional, non-negative |
| created_at | TIMESTAMP | Auto-generated |
| updated_at | TIMESTAMP | Auto-updated |

### StockMovement
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | Primary key |
| product_id | INTEGER | Foreign key to products |
| movement_type | ENUM | 'add' or 'remove' |
| quantity | INTEGER | Positive |
| previous_stock | INTEGER | Snapshot before movement |
| new_stock | INTEGER | Snapshot after movement |
| reference | VARCHAR(255) | Optional, for order/PO tracking |
| notes | VARCHAR(500) | Optional |
| created_at | TIMESTAMP | Auto-generated |

## Testing

```bash
# Run tests with test database
./run-tests.sh

# Or manually
docker-compose up -d test-db
DATABASE_URL=postgresql://test_user:test_pass@localhost:5433/test_db pytest test_main.py -v
docker-compose stop test-db
```
