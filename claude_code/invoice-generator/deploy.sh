#!/bin/bash

# Invoice Generator - Hostinger VPS Deployment Script
# Usage: ./deploy.sh [domain]

set -e

DOMAIN=${1:-"yourdomain.com"}
APP_DIR="/opt/invoice-generator"
REPO_URL="https://github.com/muralidrn09/GEN-AI-60day-challange.git"

echo "=========================================="
echo "Invoice Generator - Production Deployment"
echo "Domain: $DOMAIN"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (sudo ./deploy.sh)"
    exit 1
fi

# Step 1: Update system
log_info "Updating system packages..."
apt update && apt upgrade -y

# Step 2: Install Docker if not present
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    log_info "Docker already installed"
fi

# Step 3: Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    log_info "Installing Docker Compose..."
    apt install -y docker-compose
else
    log_info "Docker Compose already installed"
fi

# Step 4: Install Git if not present
if ! command -v git &> /dev/null; then
    log_info "Installing Git..."
    apt install -y git
fi

# Step 5: Clone or update repository
if [ -d "$APP_DIR" ]; then
    log_info "Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    log_info "Cloning repository..."
    git clone $REPO_URL /tmp/repo
    mkdir -p $APP_DIR
    cp -r /tmp/repo/claude_code/invoice-generator/* $APP_DIR/
    rm -rf /tmp/repo
fi

cd $APP_DIR/docker

# Step 6: Create SSL directory
mkdir -p nginx/ssl

# Step 7: Check/create .env.prod
if [ ! -f ".env.prod" ]; then
    log_warn "Creating .env.prod from template..."
    cp .env.prod.example .env.prod

    # Generate random passwords
    DB_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    SECRET_KEY=$(openssl rand -base64 64 | tr -dc 'a-zA-Z0-9' | head -c 64)

    # Update .env.prod with generated values
    sed -i "s/your_secure_database_password_here/$DB_PASS/" .env.prod
    sed -i "s/your_super_secret_key_here_min_32_chars/$SECRET_KEY/" .env.prod
    sed -i "s/yourdomain.com/$DOMAIN/g" .env.prod

    log_warn "Generated secure passwords in .env.prod"
    log_warn "Please update email settings manually if needed"
fi

# Step 8: Update nginx config with domain
log_info "Configuring Nginx for domain: $DOMAIN"
sed -i "s/yourdomain.com/$DOMAIN/g" nginx/nginx.prod.conf

# Step 9: Create initial nginx config without SSL (for certbot)
cat > nginx/nginx.initial.conf << 'NGINX_CONF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name _;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location /api/ {
            proxy_pass http://backend:8000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
        }
    }
}
NGINX_CONF

# Step 10: Start services with initial config (no SSL)
log_info "Starting services (initial deployment without SSL)..."
cp nginx/nginx.initial.conf nginx/nginx.prod.conf.bak
cp nginx/nginx.initial.conf nginx/nginx.prod.conf

# Load environment and start
set -a
source .env.prod
set +a

docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to start
log_info "Waiting for services to start..."
sleep 10

# Step 11: Get SSL certificate
log_info "Obtaining SSL certificate for $DOMAIN..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@$DOMAIN \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN || log_warn "SSL certificate generation failed - you may need to set up DNS first"

# Step 12: Restore full nginx config with SSL
if [ -f "nginx/ssl/live/$DOMAIN/fullchain.pem" ]; then
    log_info "SSL certificate obtained, enabling HTTPS..."
    cp nginx/nginx.prod.conf.bak nginx/nginx.prod.conf
    docker-compose -f docker-compose.prod.yml restart nginx
else
    log_warn "SSL not configured. Running on HTTP only."
    log_warn "Run this script again after DNS is configured."
fi

# Step 13: Setup auto-renewal cron job
log_info "Setting up SSL auto-renewal..."
(crontab -l 2>/dev/null | grep -v certbot; echo "0 3 * * * cd $APP_DIR/docker && docker-compose -f docker-compose.prod.yml run --rm certbot renew && docker-compose -f docker-compose.prod.yml restart nginx") | crontab -

# Step 14: Setup firewall
log_info "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
fi

# Done
echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Your Invoice Generator is now running at:"
echo "  - HTTP:  http://$DOMAIN"
echo "  - HTTPS: https://$DOMAIN (if SSL configured)"
echo ""
echo "API Documentation:"
echo "  - https://$DOMAIN/api/docs"
echo ""
echo "To view logs:"
echo "  cd $APP_DIR/docker && docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To update the application:"
echo "  cd $APP_DIR && git pull && cd docker && docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
