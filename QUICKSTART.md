# Ganjoor Django - Quick Start Guide

> 🚀 Get up and running with Ganjoor Django in minutes!

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip and venv

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The script will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Generate `.env` file with secure SECRET_KEY
- ✅ Create necessary directories
- ✅ Run migrations (optional)
- ✅ Create superuser (optional)

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy the output and paste it in .env as SECRET_KEY value

# 5. Configure database in .env
# Update DB_PASSWORD and other database settings

# 6. Run migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Collect static files
python manage.py collectstatic --noinput
```

## Configuration

Edit `.env` file with your settings:

```ini
# Essential settings
SECRET_KEY=your-generated-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=ganjoor
DB_USER=ganjoor
DB_PASSWORD=your-secure-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

## Database Setup

### PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE ganjoor;
postgres=# CREATE USER ganjoor WITH PASSWORD 'your-secure-password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE ganjoor TO ganjoor;
postgres=# \q
```

## Import Data

If you have CSV data files:

```bash
python manage.py import_ganjoor \
    --poets poets.csv \
    --cats categories.csv \
    --poems poems.csv \
    --verses verses.csv \
    --batch-size 1000
```

## Run the Server

```bash
# Development server
python manage.py runserver

# Or on a specific port
python manage.py runserver 8080

# Or bind to all interfaces
python manage.py runserver 0.0.0.0:8000
```

## Access the Application

- 🏠 **Home Page**: http://127.0.0.1:8000/
- 📚 **API Root**: http://127.0.0.1:8000/api/
- 📖 **API Docs (Swagger)**: http://127.0.0.1:8000/api/schema/swagger-ui/
- 🔧 **Admin Panel**: http://127.0.0.1:8000/admin/

## Quick API Examples

### Get All Poets

```bash
curl http://127.0.0.1:8000/api/poets/
```

### Search Poems

```bash
curl "http://127.0.0.1:8000/api/poems/search/?q=عشق"
```

### Get Poet's Poems

```bash
curl http://127.0.0.1:8000/api/poets/1/poems/
```

### Authentication (JWT)

```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your-username","password":"your-password"}'

# Use token
curl http://127.0.0.1:8000/api/favorites/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Common Tasks

### Create Superuser

```bash
python manage.py createsuperuser
```

### Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Check for Issues

```bash
python manage.py check
```

### Create Database Backup

```bash
python manage.py dumpdata > backup.json

# Or PostgreSQL backup
pg_dump ganjoor > backup.sql
```

### Load Database Backup

```bash
python manage.py loaddata backup.json

# Or PostgreSQL restore
psql ganjoor < backup.sql
```

## Development Tools

### Django Shell

```bash
python manage.py shell

# Or with enhanced shell (if django-extensions installed)
python manage.py shell_plus
```

### Database Shell

```bash
python manage.py dbshell
```

### View All URLs

```bash
python manage.py show_urls  # If django-extensions installed
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"

```bash
pip install python-dotenv
```

### "FATAL: password authentication failed"

Check your `.env` file:
- Verify `DB_PASSWORD` is correct
- Ensure PostgreSQL user exists
- Check `DB_HOST` and `DB_PORT`

### "relation does not exist"

```bash
python manage.py migrate
```

### Static files not loading

```bash
python manage.py collectstatic --noinput
```

### Port already in use

```bash
# Use a different port
python manage.py runserver 8080

# Or find and kill the process
lsof -ti:8000 | xargs kill -9  # On Linux/Mac
```

## Production Deployment

### 1. Update Settings

In `.env`:

```ini
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=generate-a-new-strong-key

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 2. Use Production Database

Update database settings with production credentials.

### 3. Use Gunicorn

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn ganjoor.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 4. Set Up Nginx (Example)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/ganjoor-django/staticfiles/;
    }

    location /media/ {
        alias /path/to/ganjoor-django/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Set Up Supervisor (Optional)

Create `/etc/supervisor/conf.d/ganjoor.conf`:

```ini
[program:ganjoor]
command=/path/to/.venv/bin/gunicorn ganjoor.wsgi:application --bind 127.0.0.1:8000 --workers 4
directory=/path/to/ganjoor-django
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ganjoor.err.log
stdout_logfile=/var/log/ganjoor.out.log
```

## Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Performance Optimization

### Enable Redis Cache

1. Install Redis:

```bash
sudo apt install redis-server  # Ubuntu/Debian
brew install redis             # macOS
```

2. Uncomment in `requirements.txt`:

```txt
django-redis==5.4.0
```

3. Install:

```bash
pip install django-redis
```

4. Update `.env`:

```ini
CACHE_BACKEND=django_redis.cache.RedisCache
REDIS_URL=redis://localhost:6379/1
```

### Database Indexes

Already optimized with `db_index=True` on frequently queried fields.

### Query Optimization

The codebase already uses:
- `select_related()` for foreign keys
- `prefetch_related()` for reverse relations
- Pagination on all list endpoints

## Monitoring (SigNoz)

Set up OpenTelemetry with SigNoz:

```ini
# In .env
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-signoz-server:4317
OTEL_SERVICE_NAME=ganjoor-django
```

## Support

- 📖 **Documentation**: See `CODE_REVIEW_IMPROVEMENTS.md`
- 🐛 **Issues**: Check logs in `logs/` directory
- 💬 **Debug**: Enable `DEBUG=True` in `.env`

## Next Steps

1. ✅ Explore the API at http://127.0.0.1:8000/api/schema/swagger-ui/
2. ✅ Import your poetry data
3. ✅ Customize templates in `core/templates/`
4. ✅ Add your custom business logic
5. ✅ Write tests in `core/tests/`

## Useful Commands Cheat Sheet

```bash
# Activate virtual environment
source .venv/bin/activate

# Run server
python manage.py runserver

# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Shell
python manage.py shell

# Check for issues
python manage.py check

# Import data
python manage.py import_ganjoor --poets poets.csv

# View logs
tail -f logs/debug.log
tail -f logs/error.log
```

---

**Happy Coding! 🎉**

For detailed information about all improvements, see `CODE_REVIEW_IMPROVEMENTS.md`.