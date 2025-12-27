from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings
from typing import List, Optional
from pathlib import Path

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME or "",
    MAIL_PASSWORD=settings.MAIL_PASSWORD or "",
    MAIL_FROM=settings.MAIL_FROM or "noreply@example.com",
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD),
    VALIDATE_CERTS=True
)


class EmailService:
    def __init__(self):
        self.fast_mail = FastMail(conf)

    async def send_invoice_email(
        self,
        to_email: str,
        invoice_number: str,
        customer_name: str,
        total: str,
        pdf_content: bytes,
        company_name: Optional[str] = None
    ) -> bool:
        """Send an invoice email with PDF attachment."""
        sender_name = company_name or settings.APP_NAME

        subject = f"Invoice {invoice_number} from {sender_name}"

        body = f"""
        <html>
        <body>
            <h2>Invoice {invoice_number}</h2>
            <p>Dear {customer_name},</p>
            <p>Please find attached your invoice for <strong>{total}</strong>.</p>
            <p>If you have any questions about this invoice, please don't hesitate to contact us.</p>
            <br>
            <p>Best regards,</p>
            <p><strong>{sender_name}</strong></p>
        </body>
        </html>
        """

        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=body,
            subtype=MessageType.html,
            attachments=[{
                "file": pdf_content,
                "filename": f"invoice_{invoice_number}.pdf",
                "type": "application/pdf"
            }]
        )

        try:
            await self.fast_mail.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    async def send_payment_reminder(
        self,
        to_email: str,
        invoice_number: str,
        customer_name: str,
        total: str,
        due_date: str,
        company_name: Optional[str] = None
    ) -> bool:
        """Send a payment reminder email."""
        sender_name = company_name or settings.APP_NAME

        subject = f"Payment Reminder: Invoice {invoice_number}"

        body = f"""
        <html>
        <body>
            <h2>Payment Reminder</h2>
            <p>Dear {customer_name},</p>
            <p>This is a friendly reminder that invoice <strong>{invoice_number}</strong>
            for <strong>{total}</strong> is due on <strong>{due_date}</strong>.</p>
            <p>If you have already made the payment, please disregard this email.</p>
            <br>
            <p>Best regards,</p>
            <p><strong>{sender_name}</strong></p>
        </body>
        </html>
        """

        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=body,
            subtype=MessageType.html
        )

        try:
            await self.fast_mail.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
