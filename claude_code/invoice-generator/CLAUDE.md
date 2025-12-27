# Invoice Generator - Claude Instructions

## Project Overview
A full-stack invoice generator MicroSaaS application with React frontend and FastAPI backend.

## Tech Stack
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15
- **Auth**: Custom JWT (access + refresh tokens)
- **PDF**: WeasyPrint with Jinja2 templates
- **Email**: FastAPI-Mail with SMTP
- **Containerization**: Docker + Docker Compose

## Project Structure
```
invoice-generator/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   ├── utils/     # Helpers (JWT, password)
│   │   └── templates/ # Invoice HTML templates
│   └── alembic/       # Database migrations
├── frontend/          # React application
│   └── src/
│       ├── api/       # API client
│       ├── components/# UI components
│       ├── pages/     # Route pages
│       ├── context/   # React context
│       └── hooks/     # Custom hooks
└── docker/            # Docker configuration
```

## Key Commands

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Docker
```bash
# Development (with hot reload)
cd docker
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose up --build
```

## API Endpoints
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/invoices` - List invoices
- `POST /api/invoices` - Create invoice
- `GET /api/invoices/{id}/pdf` - Download PDF
- `POST /api/invoices/{id}/email` - Send via email

## Features
- Customer management
- Product/service catalog
- Invoice creation with line items
- Tax calculations
- 3 invoice templates (classic, modern, minimal)
- PDF export
- Email invoices
- Payment status tracking
- Dashboard with analytics

## Environment Variables
See `.env.example` files in backend and frontend directories.
