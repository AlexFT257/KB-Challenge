# Inventory Management System

A simple inventory management API built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- Add stock (supplier deliveries)
- Remove stock (customer purchases)
- View current stock levels for all products
- Track stock movement history per product
- Full audit trail with before/after stock levels
- Prevents negative inventory
- Row-level locking for concurrent operations

## Tech Stack

- **Python 3.11**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Docker** - Containerization

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
| `POST` | `/api/inventory/add-stock` | Add stock to a product |
| `POST` | `/api/inventory/remove-stock` | Remove stock from a product |
| `GET` | `/api/inventory/stock` | Get all products stock levels |
| `GET` | `/api/inventory/movements/{sku}` | Track stock movements for a product |
| `GET` | `/api/products/{sku}` | Get product by SKU |
| `GET` | `/health` | Health check |

## Usage Examples

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
KBChallenge/
├── app/
│   ├── main.py          # FastAPI app & endpoints
│   ├── models.py        # SQLAlchemy models (Product, StockMovement)
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Business logic
│   ├── database.py      # Database connection
│   ├── config.py        # Configuration
│   └── seed_data.py     # Database seeding
├── docker-compose.yml   # Docker services
├── Dockerfile           # App container
├── init-db.sql          # Seed data SQL
└── requirements.txt     # Python dependencies
```

## Data Models

### Product
- `id`, `name`, `sku` (unique), `description`, `current_stock`, `price`
- Tracks current inventory levels

### StockMovement
- `product_id`, `movement_type` (add/remove), `quantity`
- `previous_stock`, `new_stock` - before/after snapshots
- `reference`, `notes` - for audit trail
- Full history of all inventory changes
