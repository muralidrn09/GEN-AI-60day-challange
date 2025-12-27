from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_item import InvoiceItem
from app.models.customer import Customer
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    InvoiceStatusUpdate, InvoiceSummary
)
from app.utils.dependencies import get_current_user
from app.services.tax_service import TaxService
from app.services.pdf_service import PDFService
from app.services.email_service import EmailService

router = APIRouter()


def generate_invoice_number(db: Session, user_id: int) -> str:
    """Generate a unique invoice number."""
    year = datetime.now().year
    count = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.invoice_number.like(f"INV-{year}-%")
    ).count()
    return f"INV-{year}-{count + 1:04d}"


@router.get("/", response_model=List[InvoiceSummary])
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all invoices for the current user."""
    query = db.query(Invoice).filter(Invoice.user_id == current_user.id)

    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    if search:
        query = query.filter(Invoice.invoice_number.ilike(f"%{search}%"))

    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for inv in invoices:
        customer_name = inv.customer.name if inv.customer else None
        result.append(InvoiceSummary(
            id=inv.id,
            invoice_number=inv.invoice_number,
            customer_name=customer_name,
            status=inv.status,
            total=inv.total,
            issue_date=inv.issue_date,
            due_date=inv.due_date,
            created_at=inv.created_at
        ))

    return result


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new invoice."""
    # Verify customer exists
    customer = db.query(Customer).filter(
        Customer.id == invoice_data.customer_id,
        Customer.user_id == current_user.id
    ).first()

    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Calculate totals
    totals = TaxService.calculate_invoice_totals(invoice_data.items)

    # Create invoice
    invoice = Invoice(
        user_id=current_user.id,
        customer_id=invoice_data.customer_id,
        invoice_number=generate_invoice_number(db, current_user.id),
        issue_date=invoice_data.issue_date,
        due_date=invoice_data.due_date,
        currency=invoice_data.currency,
        template=invoice_data.template,
        notes=invoice_data.notes,
        terms=invoice_data.terms,
        subtotal=totals["subtotal"],
        tax_amount=totals["tax_amount"],
        discount_amount=totals["discount_amount"],
        total=totals["total"]
    )
    db.add(invoice)
    db.flush()

    # Create invoice items
    for item_data in invoice_data.items:
        item_calc = TaxService.calculate_item_amount(
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            tax_rate=item_data.tax_rate or Decimal("0"),
            discount_percent=item_data.discount_percent or Decimal("0")
        )

        item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item_data.product_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            tax_rate=item_data.tax_rate,
            discount_percent=item_data.discount_percent,
            amount=item_calc["total"]
        )
        db.add(item)

    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific invoice."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an invoice."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    if invoice.status == InvoiceStatus.PAID.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot modify paid invoice")

    update_data = invoice_data.model_dump(exclude_unset=True, exclude={"items"})

    for field, value in update_data.items():
        setattr(invoice, field, value)

    # Update items if provided
    if invoice_data.items is not None:
        # Delete existing items
        db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()

        # Calculate new totals
        totals = TaxService.calculate_invoice_totals(invoice_data.items)
        invoice.subtotal = totals["subtotal"]
        invoice.tax_amount = totals["tax_amount"]
        invoice.discount_amount = totals["discount_amount"]
        invoice.total = totals["total"]

        # Add new items
        for item_data in invoice_data.items:
            item_calc = TaxService.calculate_item_amount(
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                tax_rate=item_data.tax_rate or Decimal("0"),
                discount_percent=item_data.discount_percent or Decimal("0")
            )

            item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item_data.product_id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                tax_rate=item_data.tax_rate,
                discount_percent=item_data.discount_percent,
                amount=item_calc["total"]
            )
            db.add(item)

    db.commit()
    db.refresh(invoice)
    return invoice


@router.patch("/{invoice_id}/status", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: int,
    status_data: InvoiceStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update invoice status."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    invoice.status = status_data.status.value

    if status_data.status == InvoiceStatus.PAID:
        invoice.paid_at = datetime.utcnow()

    db.commit()
    db.refresh(invoice)
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an invoice."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    db.delete(invoice)
    db.commit()
    return None


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download invoice as PDF."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    pdf_service = PDFService()
    pdf_content = pdf_service.generate_invoice_pdf(invoice, current_user)

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"
        }
    )


@router.post("/{invoice_id}/email")
async def email_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send invoice via email."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    if not invoice.customer or not invoice.customer.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer has no email address"
        )

    # Generate PDF
    pdf_service = PDFService()
    pdf_content = pdf_service.generate_invoice_pdf(invoice, current_user)

    # Send email
    email_service = EmailService()
    success = await email_service.send_invoice_email(
        to_email=invoice.customer.email,
        invoice_number=invoice.invoice_number,
        customer_name=invoice.customer.name,
        total=f"{invoice.currency} {invoice.total}",
        pdf_content=pdf_content,
        company_name=current_user.company_name
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

    # Update status to sent
    if invoice.status == InvoiceStatus.DRAFT.value:
        invoice.status = InvoiceStatus.SENT.value
        db.commit()

    return {"message": "Invoice sent successfully"}
