from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    unit_price: Decimal
    unit: Optional[str] = "unit"
    tax_rate: Optional[Decimal] = Decimal("0")
    sku: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[Decimal] = None
    unit: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    sku: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
