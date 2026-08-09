from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal

class StockMovementRequest(BaseModel):
    sku:str = Field(..., description="Product SKU")
    quantity:int = Field(...,gt=0, description="Must be positive")
    reference:Optional[str] = None
    notes:Optional[str] = None

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
