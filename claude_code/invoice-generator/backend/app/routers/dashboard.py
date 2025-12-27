from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.models.customer import Customer
from app.utils.dependencies import get_current_user
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter()


class DashboardStats(BaseModel):
    total_revenue: Decimal
    total_invoices: int
    paid_invoices: int
    pending_invoices: int
    overdue_invoices: int
    total_customers: int


class RevenueData(BaseModel):
    month: str
    revenue: Decimal
    count: int


class RecentInvoice(BaseModel):
    id: int
    invoice_number: str
    customer_name: str
    total: Decimal
    status: str
    due_date: str


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    # Total revenue from paid invoices
    total_revenue = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
        Invoice.user_id == current_user.id,
        Invoice.status == InvoiceStatus.PAID.value
    ).scalar()

    # Invoice counts
    total_invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).count()

    paid_invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.status == InvoiceStatus.PAID.value
    ).count()

    pending_invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.status.in_([InvoiceStatus.DRAFT.value, InvoiceStatus.SENT.value])
    ).count()

    overdue_invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.status == InvoiceStatus.OVERDUE.value
    ).count()

    # Total customers
    total_customers = db.query(Customer).filter(Customer.user_id == current_user.id).count()

    return DashboardStats(
        total_revenue=Decimal(str(total_revenue)),
        total_invoices=total_invoices,
        paid_invoices=paid_invoices,
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices,
        total_customers=total_customers
    )


@router.get("/revenue", response_model=List[RevenueData])
async def get_revenue_chart(
    months: int = Query(6, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly revenue data for chart."""
    result = []
    today = datetime.now()

    for i in range(months - 1, -1, -1):
        # Calculate month boundaries
        month_date = today - timedelta(days=i * 30)
        year = month_date.year
        month = month_date.month

        # Get revenue for this month
        revenue = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
            Invoice.user_id == current_user.id,
            Invoice.status == InvoiceStatus.PAID.value,
            extract('year', Invoice.paid_at) == year,
            extract('month', Invoice.paid_at) == month
        ).scalar()

        # Get invoice count
        count = db.query(Invoice).filter(
            Invoice.user_id == current_user.id,
            Invoice.status == InvoiceStatus.PAID.value,
            extract('year', Invoice.paid_at) == year,
            extract('month', Invoice.paid_at) == month
        ).count()

        month_name = month_date.strftime("%b %Y")
        result.append(RevenueData(
            month=month_name,
            revenue=Decimal(str(revenue)),
            count=count
        ))

    return result


@router.get("/recent", response_model=List[RecentInvoice])
async def get_recent_invoices(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent invoices."""
    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id
    ).order_by(Invoice.created_at.desc()).limit(limit).all()

    result = []
    for inv in invoices:
        result.append(RecentInvoice(
            id=inv.id,
            invoice_number=inv.invoice_number,
            customer_name=inv.customer.name if inv.customer else "N/A",
            total=inv.total,
            status=inv.status,
            due_date=inv.due_date.strftime("%Y-%m-%d")
        ))

    return result
