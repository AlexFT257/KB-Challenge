from itertools import product

from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from . import models, schemas
import logging

logger = logging.getLogger(__name__)

def get_product_by_sku(db:Session, sku: str)-> models.Product:
    """Get product with row-level lock"""
    product = db.execute(
        select(models.Product)
        .where(models.Product.sku ==sku)
        .with_for_update()
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with sku `{sku}` not found"
        )

    return product

def create_product(db: Session, product_data: schemas.ProductCreate) -> models.Product:
    # Check if SKU already exists
    existing = db.query(models.Product).filter(models.Product.sku == product_data.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )

    product = models.Product(
        name=product_data.name,
        sku=product_data.sku,
        description=product_data.description,
        current_stock=product_data.current_stock,
        price=product_data.price
    )

    db.add(product)

    # If initial stock > 0, record it as a movement
    if product_data.current_stock > 0:
        db.flush()
        movement = models.StockMovement(
            product_id=product.id,
            movement_type=models.MovementType.ADD,
            quantity=product_data.current_stock,
            previous_stock=0,
            new_stock=product_data.current_stock,
            reference="INITIAL-STOCK",
            notes="Initial inventory"
        )
        db.add(movement)

    db.commit()
    db.refresh(product)
    return product

def validate_stock_removal(product:models.Product, quantity: int)-> None:
    if product.current_stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock, Current: `{product.current_stock}`, Requested: `{quantity}`"
        )

def create_stock_movement(
    db: Session,
    product: models.Product,
    movement_type: models.MovementType,
    quantity: int,
    reference: str = None,
    notes:str = None
)-> models.StockMovement:

    previous_stock = product.current_stock
    if movement_type == models.MovementType.ADD:
        new_stock = previous_stock+quantity
    else:
        validate_stock_removal(product,quantity)
        new_stock = previous_stock - quantity

    movement = models.StockMovement(
        product_id = product.id,
        movement_type = movement_type,
        quantity = quantity,
        previous_stock = previous_stock,
        new_stock = new_stock,
        reference = reference,
        notes = notes
    )

    product.current_stock = new_stock

    db.add(movement)
    db.commit()
    db.refresh(movement)

    logger.info(
        f"Stock {movement_type.value}: SKU = {product.sku},"
        f"Quantity= {quantity}, Stock: {previous_stock}=>{new_stock}"
    )

    return movement

def add_stock(
    db: Session,
    stock_data: schemas.StockMovementRequest
)-> schemas.StockMovementResponse:
    product = get_product_by_sku(db,stock_data.sku)
    movement = create_stock_movement(
        db=db,
        product= product,
        movement_type=models.MovementType.ADD,
        quantity=stock_data.quantity,
        reference=stock_data.reference,
        notes=stock_data.notes
    )

    return schemas.StockMovementResponse.model_validate(movement)

def remove_stock(
    db: Session,
    stock_data: schemas.StockMovementRequest
)-> schemas.StockMovementResponse:
    product = get_product_by_sku(db,stock_data.sku)
    movement = create_stock_movement(
        db=db,
        product=product,
        movement_type=models.MovementType.REMOVE,
        quantity=stock_data.quantity,
        reference=stock_data.reference,
        notes=stock_data.notes
    )

    return schemas.StockMovementResponse.model_validate(movement)
