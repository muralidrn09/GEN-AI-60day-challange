from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from pathlib import Path
from io import BytesIO
from app.models.invoice import Invoice
from app.models.user import User
from datetime import datetime

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class PDFService:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    def generate_invoice_pdf(self, invoice: Invoice, user: User) -> bytes:
        """Generate a PDF for an invoice."""
        template_name = f"invoice_{invoice.template or 'classic'}.html"

        try:
            template = self.env.get_template(template_name)
        except Exception:
            template = self.env.get_template("invoice_classic.html")

        # Prepare data
        context = {
            "invoice": invoice,
            "user": user,
            "customer": invoice.customer,
            "items": invoice.items,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # Render HTML
        html_content = template.render(**context)

        # Generate PDF
        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        return pdf_buffer.getvalue()

    def get_invoice_html(self, invoice: Invoice, user: User) -> str:
        """Get the HTML content for an invoice (for preview)."""
        template_name = f"invoice_{invoice.template or 'classic'}.html"

        try:
            template = self.env.get_template(template_name)
        except Exception:
            template = self.env.get_template("invoice_classic.html")

        context = {
            "invoice": invoice,
            "user": user,
            "customer": invoice.customer,
            "items": invoice.items,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        return template.render(**context)
