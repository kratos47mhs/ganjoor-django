#!/bin/bash

# Ganjoor Django Project Setup Script
# This script helps set up the project for the first time

set -e  # Exit on error

echo "======================================"
echo "Ganjoor Django Project Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}!${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env

    # Generate a new SECRET_KEY
    echo ""
    echo "Generating SECRET_KEY..."
    NEW_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

    # Update SECRET_KEY in .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET_KEY/" .env
    fi

    echo -e "${GREEN}✓${NC} .env file created with new SECRET_KEY"
    echo -e "${YELLOW}!${NC} Please update database credentials in .env file"
else
    echo -e "${YELLOW}!${NC} .env file already exists (not overwriting)"
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    echo ""
    echo "Creating logs directory..."
    mkdir -p logs
    echo -e "${GREEN}✓${NC} logs directory created"
fi

# Create media directory if it doesn't exist
if [ ! -d "media" ]; then
    echo ""
    echo "Creating media directory..."
    mkdir -p media
    echo -e "${GREEN}✓${NC} media directory created"
fi

# Check PostgreSQL connection
echo ""
echo "Checking database configuration..."
echo -e "${YELLOW}!${NC} Make sure PostgreSQL is running and credentials in .env are correct"

# Ask if user wants to run migrations
echo ""
read -p "Do you want to run database migrations now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running migrations..."
    python manage.py makemigrations
    python manage.py migrate
    echo -e "${GREEN}✓${NC} Migrations completed"
fi

# Ask if user wants to create superuser
echo ""
read -p "Do you want to create a superuser now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    python manage.py createsuperuser
fi

# Ask if user wants to collect static files
echo ""
read -p "Do you want to collect static files now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    echo -e "${GREEN}✓${NC} Static files collected"
fi

echo ""
echo "======================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Update database credentials in .env file"
echo "2. Review and update other settings in .env as needed"
echo "3. Run 'source .venv/bin/activate' to activate virtual environment"
echo "4. Run 'python manage.py runserver' to start the development server"
echo ""
echo "For data import:"
echo "python manage.py import_ganjoor --poets poets.csv --cats cats.csv --poems poems.csv --verses verses.csv"
echo ""
echo "API Documentation will be available at:"
echo "http://127.0.0.1:8000/api/schema/swagger-ui/"
echo ""
echo "Admin panel:"
echo "http://127.0.0.1:8000/admin/"
echo ""
