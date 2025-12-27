from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceItemBase(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: Decimal = Decimal("1")
    unit_price: Decimal
    tax_rate: Optional[Decimal] = Decimal("0")
    discount_percent: Optional[Decimal] = Decimal("0")


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int
    amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    customer_id: int
    issue_date: date
    due_date: date
    currency: Optional[str] = "USD"
    template: Optional[str] = "classic"
    notes: Optional[str] = None
    terms: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    currency: Optional[str] = None
    template: Optional[str] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    items: Optional[List[InvoiceItemCreate]] = None


class InvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus


class InvoiceResponse(InvoiceBase):
    id: int
    user_id: int
    invoice_number: str
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    items: List[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvoiceSummary(BaseModel):
    id: int
    invoice_number: str
    customer_name: Optional[str] = None
    status: str
    total: Decimal
    issue_date: date
    due_date: date
    created_at: datetime
