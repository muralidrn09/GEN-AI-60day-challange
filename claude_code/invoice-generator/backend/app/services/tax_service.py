from decimal import Decimal
from typing import List
from app.schemas.invoice import InvoiceItemCreate


class TaxService:
    @staticmethod
    def calculate_item_amount(
        quantity: Decimal,
        unit_price: Decimal,
        tax_rate: Decimal = Decimal("0"),
        discount_percent: Decimal = Decimal("0")
    ) -> dict:
        """Calculate the amount for a single invoice item."""
        subtotal = quantity * unit_price
        discount_amount = subtotal * (discount_percent / Decimal("100"))
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * (tax_rate / Decimal("100"))
        total = taxable_amount + tax_amount

        return {
            "subtotal": round(subtotal, 2),
            "discount_amount": round(discount_amount, 2),
            "tax_amount": round(tax_amount, 2),
            "total": round(total, 2)
        }

    @staticmethod
    def calculate_invoice_totals(items: List[InvoiceItemCreate]) -> dict:
        """Calculate totals for an entire invoice."""
        subtotal = Decimal("0")
        total_tax = Decimal("0")
        total_discount = Decimal("0")

        for item in items:
            item_calc = TaxService.calculate_item_amount(
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate=item.tax_rate or Decimal("0"),
                discount_percent=item.discount_percent or Decimal("0")
            )
            subtotal += item_calc["subtotal"]
            total_tax += item_calc["tax_amount"]
            total_discount += item_calc["discount_amount"]

        total = subtotal - total_discount + total_tax

        return {
            "subtotal": round(subtotal, 2),
            "tax_amount": round(total_tax, 2),
            "discount_amount": round(total_discount, 2),
            "total": round(total, 2)
        }
