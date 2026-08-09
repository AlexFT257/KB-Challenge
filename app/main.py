from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.responses import JSONResponse
from . import models, schemas, crud, database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Inventory Management System",
    description="API for managing a store inventory",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    try:
        database.init_db()
        logger.info("Database Initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initializae database: {e}")
        # not raising for the health check

@app.get("/")
def read_root():
    return {
        "message": "Inventory Management System API",
        "version":"1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health":"/health",
            "add_stock": "/api/inventory/add-stock",
            "remove_stock":"/api/inventory/remove-stock",
            "get_product":"/api/products/{sku}"
        }
    }

@app.get("/health")
def health_check(db:Session = Depends(database.get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp":datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.post(
    "/api/inventory/add-stock",
    response_model=schemas.StockMovementResponse,
    status_code=status.HTTP_200_OK,
    summary="Add stock to product"
)
def add_stock_endpoint(
    stock_data: schemas.StockMovementRequest,
    db:Session = Depends(database.get_db)
):
    try:
        return crud.add_stock(db, stock_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding stock: {str(e)}"
        )

@app.post(
    "/api/inventory/remove-stock",
    response_model=schemas.StockMovementResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove stock from product"
)
def remove_stock_endpoint(
    stock_data: schemas.StockMovementRequest,
    db:Session = Depends(database.get_db)
):
    try:
        return crud.remove_stock(db, stock_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing stock: {str(e)}"
        )

@app.get(
    "/api/products/{sku}",
    response_model=schemas.ProductResponse,
    summary="Get product by sku"
)
def get_product(sku:str, db:Session = Depends(database.get_db)):
    try:
        product = crud.get_product_by_sku(db,sku)
        return schemas.ProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving products: {str(e)}"
        )

@app.get(
    "/api/inventory/stock",
    response_model=list[schemas.ProductResponse],
    summary="Get all products stock",
    description="Retrive current stock levels for all products",
    tags=["Inventory"]
)
def get_all_stock(
    pagination: schemas.PaginationParams = Depends(),
    db:Session = Depends(database.get_db)
):
    try:
        products = db.query(models.Product).offset(pagination.offset).limit(pagination.limit).all()
        return [schemas.ProductResponse.model_validate(p) for p in products]
    except Exception as e:
        logger.error(f"Error getting stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving stock: {e}"
        )


@app.get(
    "/api/inventory/movements/{sku}",
    response_model=list[schemas.StockMovementResponse],
    summary="Get stock movements for a product",
    description="Track all inventory changes (add/remove) for a specific product by sku",
    tags=["Inventory"]
)
def get_product_movements(
    sku:str,
    pagination:schemas.PaginationParams= Depends(),
    db:Session = Depends(database.get_db)
):
    try:
        # non-locking as is a read-only
        product = db.query(models.Product).filter(models.Product.sku==sku).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU '{sku}' not found"
            )

        movements = (
            db.query(models.StockMovement)
            .filter(models.StockMovement.product_id == product.id)
            .order_by(models.StockMovement.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.limit)
            .all()
        )

        return [schemas.StockMovementResponse.model_validate(m) for m in movements]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting movements for sku {sku} : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrivieng movements: {str(e)}"
        )
