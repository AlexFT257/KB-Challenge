from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal

class StockMovementRequest(BaseModel):
    sku:str = Field(..., description="Product SKU", min_length=1)
    quantity:int = Field(...,gt=0, description="Must be positive")
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

class PaginationParams(BaseModel):
    offset:int = Field(0, ge=0, description="Number of records of offset")
    limit:int = Field(100, ge=1, description="Number of records to return")
