# Invoice Generator MicroSaaS

A modern, full-stack invoice generator application built with React and FastAPI.

## Features

- **User Authentication**: Secure JWT-based authentication with access and refresh tokens
- **Customer Management**: Add, edit, and manage your customer database
- **Product Catalog**: Maintain a catalog of products and services
- **Invoice Creation**: Create professional invoices with line items, taxes, and discounts
- **Multiple Templates**: Choose from Classic, Modern, or Minimal invoice designs
- **PDF Export**: Download invoices as PDF documents
- **Email Invoices**: Send invoices directly to customers via email
- **Payment Tracking**: Track invoice status (Draft, Sent, Paid, Overdue)
- **Dashboard Analytics**: View revenue charts and business statistics

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 15 |
| Authentication | Custom JWT |
| PDF Generation | WeasyPrint |
| Email | FastAPI-Mail |
| Containerization | Docker, Docker Compose |

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Navigate to the docker directory:
   ```bash
   cd invoice-generator/docker
   ```

3. Start the development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start development server
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/invoice_db
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
```

## Project Structure

```
invoice-generator/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API routes
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   └── templates/       # Invoice templates
│   ├── alembic/             # Migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── context/         # React context
│   │   └── hooks/           # Custom hooks
│   └── package.json
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
└── README.md
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Invoice Templates

The application includes three professional invoice templates:

1. **Classic** - Clean, traditional business invoice
2. **Modern** - Contemporary design with gradient header
3. **Minimal** - Simple, elegant typography-focused design

## License

MIT License
