from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal

# PostgreSQL limits
MAX_INT = 2147483647  # PostgreSQL INTEGER max
MAX_PRICE = 99999999.99  # NUMERIC(10,2) max

class StockMovementRequest(BaseModel):
    sku:str = Field(..., description="Product SKU", min_length=1, max_length=100)
    quantity:int = Field(...,gt=0, le=MAX_INT, description="Must be positive")
    reference:Optional[str] = Field(None, max_length=255, description="Order ID, invoice, etc")
    notes:Optional[str] = Field(None, max_length=500, description="Additional notes")

class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id :int
    product_id: int
    movement_type: str
    quantity: int
    previous_stock: int
    new_stock :int
    reference :Optional[str]
    notes: Optional[str]
    created_at: datetime

class ProductResponse(BaseModel):
    model_config= ConfigDict(from_attributes=True)

    id : int
    name: str
    sku : str
    description: Optional[str]
    current_stock :int
    price :Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    current_stock: int = Field(0, ge=0, le=MAX_INT)
    price: Optional[Decimal] = Field(None, ge=0, le=MAX_PRICE, max_digits=10, decimal_places=2)

class PaginationParams(BaseModel):
    offset:int = Field(0, ge=0, le=MAX_INT, description="Number of records of offset")
    limit:int = Field(50, ge=1, le=100, description="Number of records to return")
